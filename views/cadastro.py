# Arquivo: views/cadastro_view.py

from flet import *

# Importe a sua nova classe Arquivo
from services.arquivos import Arquivo
from services.repository import TurmaRepository, PdfRepository
from components.buttons import btn_padrao
from components.pdf_preview import gerar_preview
from sqlalchemy.orm import Session

class CadastroView:
    def __init__(self, page: Page, session: Session):
        self.page = page
        self.arquivo_atual = None  # Substitui a variável 'nonlocal'

        # --- Componentes da UI (definidos como atributos da classe) ---
        self.file_picker = FilePicker(on_result=self._on_file_selected)
        self.page.overlay.append(self.file_picker)

        self.tf_titulo = TextField(label="Título do Documento", expand=True)
        self.tf_tags = TextField(label="Tags (separe por vírgula)", expand=True)
        
        self.session = session
        self.turma_repo = TurmaRepository(self.session)
        self.pdf_repo = PdfRepository(self.session)
        
        lista_opcoes = [dropdown.Option(t.nome) for t in self.turma_repo.find_all()]
        self.drop_down_turmas = Dropdown(
            label="Escolha uma turma (opcional)", options=lista_opcoes, width=300
        )

        self.pdf_preview = Container(
            content=Text("Selecione um PDF para visualizar", size=16),
            alignment=alignment.center,
            bgcolor="#f4f4f5",
            border_radius=10,
            width=250,
            height=250 * 1.414,
        )

    # --- Métodos de Construção da UI ---

    def _build_coluna_esquerda(self) -> Column:
        """Constrói a coluna da esquerda com o preview e o botão de upload."""
        return Column(
            controls=[
                self.pdf_preview,
                btn_padrao("Upload", lambda _: self.file_picker.pick_files()),
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
                            Text("Turma:", weight="bold", size=20),
                            Row(
                                controls=[
                                    self.drop_down_turmas,
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
            alignment="center"
        )

    # --- Métodos de Evento (Handlers) ---

    def _on_file_selected(self, e: FilePickerResultEvent):
        """Chamado quando um arquivo é selecionado no FilePicker."""
        caminho_temp = Arquivo.copiar_para_temp(e, self.page)
        if not caminho_temp:
            return  # Usuário cancelou a seleção

        # Usa a classe Arquivo para criar o objeto e extrair os dados
        self.arquivo_atual = Arquivo.from_pdf(caminho_temp)

        # Atualiza os campos da UI com os dados extraídos
        self._atualizar_campos_e_preview()

    def _on_save_button(self, e):
        """Salva o arquivo permanentemente e limpa a tela."""
        if self.arquivo_atual:
            try:
                # Pega os valores dos campos, caso o usuário tenha editado
                self.arquivo_atual.titulo = self.tf_titulo.value
                self.arquivo_atual.tags = [
                    tag.strip() for tag in self.tf_tags.value.split(",")
                ]

                # Salva o arquivo e atualiza o caminho
                self.arquivo_atual.salvar_definitivo()
                
                # TODO: Aqui você adicionaria a lógica para salvar no banco de dados
                # ex: database.salvar_arquivo(self.arquivo_atual, self.drop_down_turmas.value)

                self.page.snack_bar = SnackBar(
                    Text(f"Arquivo '{self.arquivo_atual.titulo}' salvo com sucesso!"),
                    open=True,
                )
                self._limpar_tela()  # Limpa os campos para um novo cadastro
            except Exception as ex:
                self.page.snack_bar = SnackBar(Text(f"Erro ao salvar: {ex}"), open=True)

            self.page.update()

    def _on_cancel_button(self, e):
        # TODO: Implementar lógica de cancelamento (ex: limpar tela, voltar pra home)
        print("Operação cancelada.")
        self._limpar_tela()

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
        self.drop_down_turmas.value = None
        self.pdf_preview.content = Text("Selecione um PDF para visualizar", size=16)
        self.page.update()

    def build(self) -> View:
        """Constrói e retorna o objeto View final para o Flet."""
        return View(
            route="/cadastro",
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
