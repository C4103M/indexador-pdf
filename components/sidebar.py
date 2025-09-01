from flet import Container, Row, Image, Text, Column, MainAxisAlignment, padding

def sidebar():
    home = Container(
        content=Row(
            controls=[Image("./elements/home.png", width=20, height=20), Text("Home", weight="bold")],
            alignment=MainAxisAlignment.START,
        ),
        width=250,
        height=30,
        padding=padding.only(left=5),
    )

    arquivos = Container(
        content=Row(
            controls=[Image("./elements/pasta.png", width=20, height=20), Text("Arquivos", weight="bold")],
            alignment=MainAxisAlignment.START,
        ),
        width=250,
        height=40,
        padding=padding.only(left=5),
    )

    configuracoes = Container(
        content=Row(
            controls=[Image("./elements/config.png", width=20, height=20), Text("Configurações", weight="bold")],
            alignment=MainAxisAlignment.START,
        ),
        width=250,
        height=40,
        padding=padding.only(left=5),
    )

    return Column(controls=[home, arquivos, configuracoes], width=250)
