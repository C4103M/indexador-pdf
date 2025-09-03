from flet import ElevatedButton, ButtonStyle, RoundedRectangleBorder

def btn_padrao(titulo_btn ,on_click):
    titulo_btn = str(titulo_btn)
    return ElevatedButton(
        titulo_btn,
        on_click=on_click,
        width=100,
        height=40,
        style=ButtonStyle(
            bgcolor={"": "#292524"},
            color={"": "white"},
            shape={"": RoundedRectangleBorder(radius=10)},
        ),
    )
