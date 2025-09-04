import os
import re
import shutil
import uuid
import yake
from PyPDF2 import PdfReader
from flet import FilePickerResultEvent, SnackBar, Text

class Arquivo:
    def __init__(self, path: str, titulo: str, tags: list = None):
        self.id = str(uuid.uuid4())
        self.path = path
        self.titulo = titulo
        self.tags = tags if tags is not None else []

    @staticmethod
    def _limpar_texto(texto: str) -> str:
        """Método estático privado para limpar e normalizar o texto extraído do PDF."""
        texto = texto.replace("\n", " ").replace("\t", " ")
        texto = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", "", texto)
        texto = re.sub(r"\s+", " ", texto)
        texto = texto.strip()
        return texto.lower()

    @staticmethod
    def _extrair_tags(conteudo: str) -> list:
        """Método estático privado para extrair palavras-chave (tags) do texto."""
        kw_extractor = yake.KeywordExtractor(lan="pt", n=2, top=5)
        tags_com_score = kw_extractor.extract_keywords(conteudo)
        # Extrai apenas a tag (palavra), ignorando o score de relevância
        tags = [tag for tag, score in tags_com_score]
        return tags

    @classmethod
    def from_pdf(cls, caminho_pdf: str):
        """
        Método de classe (factory) que cria uma instância de Arquivo 
        a partir de um arquivo PDF, extraindo seu conteúdo e metadados.
        """
        reader = PdfReader(caminho_pdf)
        
        # Tenta extrair o título dos metadados, senão, usa o nome do arquivo
        titulo = reader.metadata.title
        if not titulo:
            titulo = os.path.splitext(os.path.basename(caminho_pdf))[0]
            
        # Extrai o texto de todas as páginas
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() or ""
            
        # Limpa o texto e extrai as tags
        texto_limpo = cls._limpar_texto(texto_completo)
        tags = cls._extrair_tags(texto_limpo)
        
        # Retorna uma nova instância da classe com os dados extraídos
        return cls(path=caminho_pdf, titulo=titulo, tags=tags)

    def salvar_definitivo(self, destino_dir="pdfs"):
        """
        Move o arquivo da sua localização atual (temporária) para a pasta
        de destino final e atualiza o caminho (path) do objeto.
        """
        if not os.path.exists(self.path):
            # Lançar um erro ou tratar caso o arquivo de origem não exista
            raise FileNotFoundError(f"O arquivo de origem não foi encontrado em: {self.path}")

        nome_arquivo = os.path.basename(self.path)
        destino_final = os.path.join(destino_dir, nome_arquivo)
        
        os.makedirs(destino_dir, exist_ok=True)
        shutil.move(self.path, destino_final)
        
        # Atualiza o path do objeto para a nova localização
        self.path = destino_final
        print(f"Arquivo movido para: {self.path}")

    @staticmethod
    def copiar_para_temp(e: FilePickerResultEvent, page):
        """
        Método estático para lidar com o evento de seleção de arquivo.
        Copia o arquivo selecionado para uma pasta temporária.
        """
        if not e.files:
            return None
        
        arquivo_selecionado = e.files[0]
        origem = arquivo_selecionado.path
        destino_dir = "pdfs/temp"
        
        os.makedirs(destino_dir, exist_ok=True)
        
        path_temporario = os.path.join(destino_dir, arquivo_selecionado.name)
        shutil.copy(origem, path_temporario)

        # Feedback visual para o usuário
        page.snack_bar = SnackBar(Text(f"Arquivo '{arquivo_selecionado.name}' carregado."), open=True)
        page.update()
        
        return path_temporario