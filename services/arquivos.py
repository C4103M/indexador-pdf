import os, re, shutil, time, uuid, yake
from PyPDF2 import PdfReader
from flet import FilePickerResultEvent, SnackBar, Text
from pathlib import Path
from appdirs import user_data_dir
from services.config import standard_dir, dir_temp, dir_pdfs


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
        Cria instância de Arquivo a partir de um PDF.
        Usa 'with open' para garantir leitura correta no exe.
        """
        try:
            caminho_pdf = Path(caminho_pdf).resolve()  # caminho absoluto
            print(caminho_pdf)
            with open(caminho_pdf, "rb") as f:
                reader = PdfReader(f)
                titulo = reader.metadata.title if reader.metadata.title else caminho_pdf.stem

                texto_completo = ""
                for page in reader.pages:
                    texto_completo += page.extract_text() or ""

            texto_limpo = cls._limpar_texto(texto_completo)
            tags = cls._extrair_tags(texto_limpo)

            return cls(path=str(caminho_pdf), titulo=titulo, tags=tags)
        except Exception as e:
            import traceback
            print("Erro no from_pdf:", e)
            traceback.print_exc()
            return None
    
    def salvar_definitivo(self):
        """
        Move ou copia o arquivo para a pasta definitiva de PDFs,
        garantindo que o nome seja sempre único (UUID).
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"O arquivo de origem não foi encontrado em: {self.path}")

        # 1. Define pastas padrão
        dir_pdfs = Path(standard_dir) / "pdfs"
        dir_temp = dir_pdfs / "temp"
        dir_pdfs.mkdir(parents=True, exist_ok=True)

        # 2. Gera nome único para o arquivo
        _, extensao = os.path.splitext(self.path)
        nome_final_unico = f"{uuid.uuid4()}{extensao}"
        destino_final = dir_pdfs / nome_final_unico

        # 3. Decide entre mover ou copiar
        caminho_origem = Path(self.path)
        if dir_temp in caminho_origem.parents:
            # Caso 1: arquivo veio do temp -> move
            shutil.move(caminho_origem, destino_final)
        else:
            # Caso 2: arquivo veio do PC do usuário -> copia
            shutil.copy(caminho_origem, destino_final)

        # 4. Atualiza o caminho interno
        self.path = str(destino_final)
        print(f"Arquivo salvo com nome único em: {self.path}")

    @staticmethod
    def copiar_para_temp(e: FilePickerResultEvent, page):
        """
        Copia arquivo selecionado para a pasta temporária em AppData.
        """
        if not e.files:
            return None

        arquivo_selecionado = e.files[0]
        origem = Path(arquivo_selecionado.path)
        destino_path = dir_temp / arquivo_selecionado.name

        shutil.copy(origem, destino_path)

        # Feedback visual
        snack_bar = SnackBar(Text(f"Arquivo '{arquivo_selecionado.name}' carregado."), open=True)
        page.open(snack_bar)

        return str(destino_path)