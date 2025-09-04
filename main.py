import flet as ft
from components.pdf_preview import gerar_preview  # sua função que retorna um Image

def main(page: ft.Page):
    # gerar preview de um PDF
    preview = gerar_preview("pdfs/temp\\Conferência -_Metropole (2023).pdf")

    # colocar dentro de um Column
    col = ft.Column(controls=[preview])

    # adicionar à página
    page.add(col)

ft.app(target=main)
