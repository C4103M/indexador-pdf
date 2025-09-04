import os
import re
import yake
import shutil
from flet import FilePickerResultEvent, SnackBar, Text, Colors
from PyPDF2 import PdfReader
import uuid


def salvar_arquivo(e: FilePickerResultEvent, page):
    # Pega o primeiro arquivo
    f = e.files[0]
    dir_origem = "pdfs"
    subdir_origem = "temp"
    origem = os.path.join(dir_origem, subdir_origem, f.name)
    destino_dir = "pdfs"
    # Garante que a pasta existe
    os.makedirs(destino_dir, exist_ok=True)
    # Monta o caminho final (pdfs/arquivo.pdf)
    destino = os.path.join(destino_dir, f.name)
    # Move o arquivo para o destino
    # print(f"Origem: {origem}\nDestino: {destino}")
    shutil.move(origem, destino)

    
def salvar_arquivo_temp(e: FilePickerResultEvent, page):
    if not e.files:  # caso o usuário cancele a seleção
        return
    
    f = e.files[0]  # pega apenas o primeiro arquivo
    origem = f.path
    destino_dir = "pdfs/temp"
    os.makedirs(destino_dir, exist_ok=True)  # cria pasta se não existir
    destino = os.path.join(destino_dir, f.name)

    shutil.copy(origem, destino)
    

    # feedback visual
    page.snack_bar = SnackBar(Text(f"Arquivo salvo em {destino}"), open=True)
    page.snack_bar.open = True
    page.update()
    
    return destino

def limpar_texto(texto: str) -> str:
    # troca quebras de linha e tabs por espaço
    texto = texto.replace("\n", " ").replace("\t", " ")
    # remove caracteres especiais (mantém letras, números e acentos)
    texto = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", "", texto)
    # compacta múltiplos espaços
    texto = re.sub(r"\s+", " ", texto)
    # remove espaços no início/fim
    texto = texto.strip()
    # tudo minúsculo
    return texto.lower()
    
def extrair_tags(conteudo):
    kw_extractor = yake.KeywordExtractor(lan="pt", n=2, top=5)
    # ATENÇÃO: Converte para o tipo lista, e retorna o nível de relevância junto
    tags = kw_extractor.extract_keywords(conteudo)
    tags = [t[0] for t in tags]
    return tags

def get_data_pdf(caminho):
    """
    Retorna os dados para ser incluídos no banco de dados.
    """
    caminho = str(caminho)
    reader = PdfReader(caminho)
    titulo = reader.metadata.title
    if titulo is None:
        titulo = os.path.splitext(os.path.basename(caminho))[0]
    tags = ""
    for i in range(len(reader.pages)):
        tags += reader.pages[i].extract_text()
    tags = limpar_texto(tags)
    tags = extrair_tags(tags)
    result = {"caminho": caminho, "titulo": titulo, "tags": tags}
    return result
