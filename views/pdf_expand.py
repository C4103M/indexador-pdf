from flet import (
    Page,
    IconButton,
    Row,
    Column,
    Icons,
    dropdown,
    alignment,
    Dropdown,
    AlertDialog,
    Text,
    TextField,
    TextButton,
    SnackBar,
    View,
    Container,
    MainAxisAlignment,
    CrossAxisAlignment,
    Colors,
    FilePicker,
    FilePickerResultEvent,
    AppBar,
    FontWeight
    
)
from sqlalchemy.orm import Session
from components.pdf_preview import gerar_preview
from services.repository import PdfRepository, AgrupamentoRepository
from components.back_btn import BackButton
import shutil
import os
import platform
import subprocess

class PdfPage:
    def __init__(self, page: Page, session: Session, pdf_id):
        self.page = page
        self.session = session
        self.pdf_id = pdf_id

        self.pdf_repo = PdfRepository(self.session)
        self.dados_pdf = self.pdf_repo.find_by_id(self.pdf_id)
        self.caminho = self.dados_pdf["caminho"]
        self.titulo = self.dados_pdf["titulo"]
        
        self.pdf_preview = gerar_preview(
            caminho_pdf=self.caminho, width=300
        )  # aqui você injeta a função que já retorna o preview

        self.nome_arquivo = self.dados_pdf["titulo"]

        self.back = BackButton(self.page, self.session)

        # FilePicker
        self.file_picker = FilePicker(on_result=self.salvar)
        self.page.overlay.append(self.file_picker)
        # Botões
        self.btn_editar = IconButton(
            icon=Icons.EDIT, on_click=lambda _: self.editar(), bgcolor=Colors.GREY_100
        )
        self.btn_excluir = IconButton(
            icon=Icons.DELETE,
            on_click=lambda _: self.excluir(),
            bgcolor=Colors.GREY_100,
        )
        self.btn_salvar = IconButton(
            icon=Icons.DOWNLOAD,
            on_click=lambda _: self.file_picker.save_file(
                dialog_title="Salvar PDF",
                file_name=f"{self.titulo}.pdf",
                allowed_extensions=["pdf"]
        ),
            bgcolor=Colors.GREY_100,
        )
        self.btn_abrir = IconButton(
            icon=Icons.OPEN_IN_NEW,
            on_click=lambda _: self.abrir(),
            bgcolor=Colors.GREY_100,
        )

        self.agrupamento_repo = AgrupamentoRepository(self.session)
        lista_opcoes = [
            dropdown.Option(t.nome) for t in self.agrupamento_repo.find_all()
        ]
        self.drop_down_agrupamentos = Dropdown(
            label="Escolha uma agrupamento (opcional)", options=lista_opcoes, width=300
        )
        self.col_esquerda = Column(
            controls=[
                # Preview do PDF
                Row(
                    controls=[self.pdf_preview],
                    alignment=MainAxisAlignment.CENTER,
                ),
            ],
            expand=True,  # coluna ocupa o espaço pai
            alignment=MainAxisAlignment.CENTER,  # centro vertical dentro da coluna
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        self.col_direita = Column(
            controls=[
                # Nome do arquivo
                Text(self.nome_arquivo, size=16, weight="bold"),
                # Botões
                Row(
                    controls=[
                        self.btn_salvar,
                        self.btn_abrir,
                        self.btn_editar,
                        self.btn_excluir,
                    ],
                ),
            ],
            expand=True,
            alignment=MainAxisAlignment.CENTER,
        )

        self.txt_edit_titulo = TextField(
            label=Text("Editar Título"), value=self.dados_pdf["titulo"]
        )
        self.txt_edit_tag = TextField(
            label=Text("Editar Tags"), value=", ".join(self.dados_pdf["tags"])
        )
        

    def editar(self):
        self.page.go(f"/edit/{self.pdf_id}")


    def excluir(self):
        # Confirmação de exclusão
        self.dlg = AlertDialog(
            title=Text("Excluir arquivo?"),
            content=Text("Tem certeza que deseja excluir este PDF?"),
            actions=[
                TextButton("Cancelar", on_click=lambda e: self.page.close(self.dlg)),
                TextButton("Excluir", on_click=lambda e: self.confirmar_exclusao()),
            ],
        )
        self.page.open(self.dlg)

    def confirmar_exclusao(self):
        self.page.close(self.dlg)
        self.page.update()
        self.pdf_repo.delete(self.pdf_id)
        self.back.go_back()
        

    def salvar(self, e: FilePickerResultEvent):
        if e.path:
            shutil.copy(self.caminho, e.path)
            self.snack_bar = SnackBar(Text(f"Arquivo salvo em: {e.path}"))
            self.page.open(self.snack_bar)
        else:
            print("Usuário cancelou")

    def abrir(self):
        caminho = self.caminho
        if platform.system() == "Windows":
            os.startfile(caminho)  # Windows
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", caminho])
        else:  # Linux
            subprocess.call(["xdg-open", caminho])

    def build(self) -> Column:
        return View(
            appbar=AppBar(
                leading=self.back.build(),
                title=Text("Gerenciar Arquivo", size=20, weight=FontWeight.BOLD),
            ),
            controls=[
                Row(
                    controls=[self.col_esquerda, self.col_direita],
                    expand=True,
                    spacing=40,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
            ]
        )


def pdf_expand_view(page: Page, session: Session, pdf_id):
    return PdfPage(page, session, pdf_id).build()
