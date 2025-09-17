# Arquivo: views/cadastro_view.py

from flet import *

# Importe a sua nova classe Arquivo
from services.arquivos import Arquivo
from services.repository import AgrupamentoRepository, PdfRepository
from components.buttons import btn_padrao
from components.pdf_preview import gerar_preview
from sqlalchemy.orm import Session
from components.progress import LoadingOverlay
from pathlib import Path
import threading
from components.back_btn import BackButton
class CadastroView:
    def __init__(self, page: Page, session: Session):
        self.page = page
        self.arquivo_atual = None  # Substitui a variável 'nonlocal'

        # --- Componentes da UI (definidos como atributos da classe) ---
        self.file_picker = FilePicker(on_result=self._on_file_selected)
        self.page.overlay.append(self.file_picker)
        
        self.directory_picker = FilePicker(on_result=self._on_directory_selected)
        self.page.overlay.append(self.directory_picker)
        
        self.tf_titulo = TextField(label="Título do Documento", expand=True)
        self.tf_tags = TextField(label="Tags (separe por vírgula)", expand=True)

        self.loading_overlay = LoadingOverlay(page)
        self.page.overlay.append(self.loading_overlay.build())
        
        self.session = session
        self.agrupamento_repo = AgrupamentoRepository(self.session)
        self.pdf_repo = PdfRepository(self.session)

        lista_opcoes = [dropdown.Option(t.nome) for t in self.agrupamento_repo.find_all()]
        self.drop_down_agrupamentos = Dropdown(
            label="Escolha uma agrupamento (opcional)", options=lista_opcoes, width=300
        )

        self.pdf_preview = Container(
            content=Text("Selecione um PDF para visualizar", size=16),
            alignment=alignment.center,
            bgcolor="#f4f4f5",
            border_radius=10,
            width=250,
            height=250 * 1.414,
        )

        self.voltar = BackButton(self.page, self.session)
        self.voltar = self.voltar.build()

    # --- Métodos de Construção da UI ---

    def _build_coluna_esquerda(self) -> Column:
        """Constrói a coluna da esquerda com o preview e o botão de upload."""
        return Column(
            controls=[
                self.pdf_preview,
                Row(
                    controls=[
                        btn_padrao("Upload", lambda _: self.file_picker.pick_files()),
                        btn_padrao("Salvar Em lote", lambda _: self.directory_picker.get_directory_path()),
                    ]
                )
            ],
            alignment="center",
        )

    def _build_coluna_direita(self) -> Column:
        """Constrói a coluna da direita com os campos de texto e botões de ação."""
        btn_salvar = btn_padrao("Salvar", self._on_save_button)
        btn_cancelar = btn_padrao("Cancelar", self._on_cancel_button)
        btn_cancelar.bgcolor = "#f3f3f3"
        btn_cancelar.color = "#000000"

        return Column(
            controls=[
                Text("Cadastrar PDF", size=40, weight="bold"),
                Container(
                    Column(
                        controls=[
                            Text("Título:", weight="bold", size=20),
                            self.tf_titulo,
                            Text("Tags:", weight="bold", size=20),
                            self.tf_tags,
                            Text("Agrupamento:", weight="bold", size=20),
                            Row(
                                controls=[
                                    self.drop_down_agrupamentos,
                                    btn_cancelar,
                                    btn_salvar,
                                ],
                                spacing=10,
                            ),
                        ]
                    ),
                    height=300,
                    padding=padding.only(left=20),
                ),
            ],
            spacing=20,
            expand=True,
            alignment="center",
        )

    # --- Métodos de Evento (Handlers) ---

    def _on_file_selected(self, e: FilePickerResultEvent):
        """Chamado quando um arquivo é selecionado no FilePicker.""" 
        caminho_temp = Arquivo.copiar_para_temp(e, self.page)
        if not caminho_temp:
            # snack_bar = SnackBar(Text(f"Falha ao abrir o arquivo"), open=True)
            # self.page.open(snack_bar)
            return  # Usuário cancelou a seleção
        
        # Usa a classe Arquivo para criar o objeto e extrair os dados
        self.arquivo_atual = Arquivo.from_pdf(caminho_temp)
        
        # Atualiza os campos da UI com os dados extraídos
        self._atualizar_campos_e_preview()
        

    def _on_save_button(self, e):
        """Salva o arquivo permanentemente e limpa a tela."""
        # print("Está chegando aqui!")
        if self.arquivo_atual:
            try:
                # print("Está chegando aqui!")
                # Pega os valores dos campos, caso o usuário tenha editado
                self.arquivo_atual.titulo = self.tf_titulo.value
                self.arquivo_atual.tags = [
                    tag.strip() for tag in self.tf_tags.value.split(",")
                ]
                self.arquivo_atual.agrupamento = self.drop_down_agrupamentos.value

                # Salva o arquivo e atualiza o caminho
                self.arquivo_atual.salvar_definitivo()
                # Salvar em banco de dados
                self.pdf_repo.create(
                    titulo=self.arquivo_atual.titulo,
                    caminho=self.arquivo_atual.path,
                    tags_valores=self.arquivo_atual.tags,
                    agrupamento_nome=self.arquivo_atual.agrupamento,
                )

                snack_bar = SnackBar(
                    Text(f"Arquivo '{self.arquivo_atual.titulo}' salvo com sucesso!"),
                    open=True,
                )
                self.page.open(snack_bar)
                self._limpar_tela()  # Limpa os campos para um novo cadastro
            except Exception as ex:
                snack_bar = SnackBar(Text(f"Erro ao salvar: {ex}"), open=True)
                self.page.open(snack_bar)
            self.page.update()

    def _on_cancel_button(self, e):
        # TODO: Implementar lógica de cancelamento (ex: limpar tela, voltar pra home)
        print("Operação cancelada.")
        self._limpar_tela()
        
    def _on_directory_selected(self, e: FilePickerResultEvent):
        """
        Gerenciador de resultado: chamado quando o usuário escolhe uma pasta.
        Ele apenas inicia a thread de trabalho.
        """
        if not e.path:
            # Usuário cancelou
            return
        
        # Mostra o overlay e inicia a thread "trabalhadora"
        self.loading_overlay.show()
        
        thread = threading.Thread(
            target=self._worker_salvar_em_lotes, 
            args=[e.path], 
            daemon=True
        )
        thread.start()
    
    def _worker_salvar_em_lotes(self, caminho_da_pasta: str):
        """Esta função roda em uma thread separada. Ela conta os PDFs, processa um a um e atualiza a barra de progresso."""
        try:
            # Listar arquivos
            print(f"Buscando arquivos pdf em: {caminho_da_pasta}")
            pasta = Path(caminho_da_pasta)
            lista_de_pdfs = list(pasta.glob("*.pdf"))
            total_de_pdfs = len(lista_de_pdfs)
            
            if total_de_pdfs == 0:
                self.page.run_threadsafe(self.page.open, SnackBar(Text("Nenhum arquivo .pdf encontrado na pasta.")))
                return
            sucessos = 0
            falhas = 0
            
            # O i recebe o índice do objeto, e o caminho_pdf_obj recebe o pdf
            for i, caminho_pdf_obj in enumerate(lista_de_pdfs):
                # Atualiza a barra de progresso
                percentual = (i + 1)/total_de_pdfs
                nome_arquivo = caminho_pdf_obj.name
                msg_progresso = f"Processando {i+1}/{total_de_pdfs}: {nome_arquivo}"
                self.page.run_thread(self.loading_overlay.set_progress, percentual)
                # Extrai os dados do pdf
                try:
                    caminho_str = str(caminho_pdf_obj)
                    
                    # Extrai os dados do PDF
                    arquivo_obj = Arquivo.from_pdf(caminho_str)
                    
                    arquivo_obj.salvar_definitivo()
                    
                    # Salva no banco de dados
                    self.pdf_repo.create(
                        titulo=arquivo_obj.titulo,
                        caminho=arquivo_obj.path,
                        tags_valores=arquivo_obj.tags,
                    )
                    sucessos += 1
                    print(f"SUCESSO: {nome_arquivo}")
                
                except Exception as e:
                    falhas += 1
                    print(f"FALHA ao processar {nome_arquivo}: {e}")
                    
            msg_final = f"Concluído! {sucessos} salvos, {falhas} falhas."
            self.page.run_thread(self.page.open, SnackBar(Text(msg_final)))
            
        finally:
            # GARANTE QUE O OVERLAY SEJA ESCONDIDO
            self.page.run_thread(self.loading_overlay.hide)
            
            
            
            
            
            
    # --- Métodos Auxiliares ---

    def _atualizar_campos_e_preview(self):
        """Atualiza os TextFields e o preview com os dados do arquivo."""
        if not self.arquivo_atual:
            return

        self.tf_titulo.value = self.arquivo_atual.titulo
        self.tf_tags.value = ", ".join(self.arquivo_atual.tags)

        # Atualiza o preview
        self.pdf_preview.content = gerar_preview(self.arquivo_atual.path)
        self.page.update()

    def _limpar_tela(self):
        """Reseta a tela para o estado inicial."""
        self.arquivo_atual = None
        self.tf_titulo.value = ""
        self.tf_tags.value = ""
        self.drop_down_agrupamentos.value = None
        self.pdf_preview.content = Text("Selecione um PDF para visualizar", size=16)
        self.page.update()

    def build(self) -> View:
        """Constrói e retorna o objeto View final para o Flet."""
        return View(
            route="/cadastro",
            appbar=AppBar(
                leading=self.voltar,
                title=Text("Cadastrar Pdf"),
                # bgcolor=Colors.ON_SURFACE_VARIANT
            ),
            controls=[
                Row(
                    controls=[
                        self._build_coluna_esquerda(),
                        self._build_coluna_direita(),
                    ],
                    expand=True,
                    spacing=40,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                )
            ],
            padding=padding.all(40),
        )


def cadastro_view(page: Page, session: Session) -> View:
    return CadastroView(page, session).build()
