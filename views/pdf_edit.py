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
import time
import threading
from components.back_btn import BackButton
class EditView:
    def __init__(self, page: Page, session: Session, pdf_id):
        self.page = page
        self.session = session
        self.pdf_id = pdf_id
        

        self.agrupamento_repo = AgrupamentoRepository(self.session)
        self.pdf_repo = PdfRepository(self.session)

        self.data = self.pdf_repo.find_by_id(self.pdf_id)
        
        self.tf_titulo = TextField(label="Título do Documento", value=self.data["titulo"],expand=True)
        self.tf_tags = TextField(label="Tags (separe por vírgula)", value=", ".join(self.data["tags"]), expand=True)
        
        self.back = BackButton(self.page, self.session)
        
        lista_opcoes = [dropdown.Option(t.nome) for t in self.agrupamento_repo.find_all()]
        self.drop_down_agrupamentos = Dropdown(
            label="Escolha uma agrupamento (opcional)", options=lista_opcoes, width=300
        )

        self.pdf_preview = gerar_preview(caminho_pdf=self.data["caminho"])

        self.voltar = BackButton(self.page, self.session)
        self.voltar = self.voltar.build()

    # --- Métodos de Construção da UI ---

    def _build_coluna_esquerda(self) -> Column:
        """Constrói a coluna da esquerda com o preview e o botão de upload."""
        return Column(
            controls=[
                self.pdf_preview,
            ],
            alignment="center",
        )

    def _build_coluna_direita(self) -> Column:
        """Constrói a coluna da direita com os campos de texto e botões de ação."""
        btn_salvar = btn_padrao("Atualizar", self._on_atualize_button)
        btn_cancelar = btn_padrao("Cancelar", self._voltar)
        btn_cancelar.bgcolor = "#f3f3f3"
        btn_cancelar.color = "#000000"

        return Column(
            controls=[
                Text("Editar PDF", size=40, weight="bold"),
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

    def _on_atualize_button(self, e):
        """Atualizar no banco de dados"""
        titulo = self.tf_titulo.value
        tags = [
            tag.strip() for tag in self.tf_tags.value.split(",")
        ]
        agrupamento = self.drop_down_agrupamentos.value or None
        # Atualizar no banco de dados
        self.pdf_repo.update(
            pdf_id=self.pdf_id,
            novo_titulo=titulo,
            novas_tags=tags,
            novo_agrupamento=agrupamento
        )
        snack_bar = SnackBar(
            Text(f"Arquivo '{titulo}' atualizado com sucesso!"),
            open=True,
        )
        self.page.open(snack_bar)
        self._voltar  # Volta a tela
        self.page.update()

    def _voltar(self, e):
        self.back.go_back()
        
    

    def build(self) -> View:
        """Constrói e retorna o objeto View final para o Flet."""
        return View(
            route="/cadastro",
            appbar=AppBar(
                leading=self.voltar,
                title=Text("Editar Pdf"),
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


def edit_view(page: Page, session: Session, pdf_id) -> View:
    return EditView(page, session, pdf_id).build()
