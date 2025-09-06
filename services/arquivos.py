import os, re, shutil, time, uuid, yake
from PyPDF2 import PdfReader
from flet import FilePickerResultEvent, SnackBar, Text
from pathlib import Path
class Arquivo:
    def __init__(self, path: str, titulo: str, tags: list = None, turma: str = None):
        self.id = str(uuid.uuid4())
        self.path = path
        self.titulo = titulo
        self.tags = tags if tags is not None else []
        self.turma = turma

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
        Move o arquivo para o destino final, garantindo que o nome seja
        sempre um identificador único (UUID).
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"O arquivo de origem não foi encontrado em: {self.path}")

        # 1. Pega a extensão do arquivo que está no caminho temporário
        _, extensao = os.path.splitext(self.path)
        
        # 2. Gera um novo nome de arquivo único e aleatório
        nome_final_unico = f"{str(uuid.uuid4())}{extensao}"

        # 3. Monta o caminho de destino final e move o arquivo
        destino_final = os.path.join(destino_dir, nome_final_unico)
        
        os.makedirs(destino_dir, exist_ok=True)
        # shutil.move(self.path, destino_final)
        
        caminho_origem = Path(self.path)
        pasta_temp = Path("pdfs/temp")
        # parents é um método do pathlib pra verificar se um arquivo está dentro de uma pasta
        if pasta_temp in caminho_origem.parents:
            # CASO 1: O arquivo está na pasta temp (fluxo de upload único)
            shutil.move(caminho_origem, destino_final)
        else:
            # CASO 2: O arquivo está em uma pasta no pc do cliente
            shutil.copy(self.path, destino_final)
        
        # 4. ATUALIZA o caminho no objeto para refletir o novo nome e local
        self.path = destino_final
        print(f"Arquivo salvo com nome único em: {self.path}")

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
        snack_bar = SnackBar(Text(f"Arquivo '{arquivo_selecionado.name}' carregado."), open=True)
        page.open(snack_bar)
        return path_temporario