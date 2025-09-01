from flet import View, Row, Column, Text, Container, TextField, ButtonStyle, RoundedRectangleBorder, alignment, padding
from flet import FilePicker, FilePickerResultEvent, SnackBar

def cadastro_view(page):
    def on_file_selected(e: FilePickerResultEvent):
        msg = f"Arquivo escolhido: {e.files[0].name}" if e.files else "Nenhum arquivo selecionado."
        page.snack_bar = SnackBar(Text(msg), open=True)
        page.update()

    file_picker = FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    pdf_preview = Container(
        content=Text("Preview do PDF selecionado", size=16, weight="bold"),
        alignment=alignment.center,
        bgcolor="#f4f4f5",
        border_radius=10,
        width=250,
        height=250 * 1.414,
    )

    col_esquerda = Column(controls=[pdf_preview], alignment="center")

    col_direita = Column(
        controls=[
            TextField(label="Título do Documento", expand=True),
            TextField(label="Tags (separe por vírgula)", expand=True),
        ],
        spacing=20,
        expand=True,
    )

    return View(
        route="/cadastro",
        controls=[Row(controls=[col_esquerda, col_direita], expand=True, spacing=40)],
        padding=padding.all(40),
    )
