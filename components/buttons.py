from flet import ElevatedButton, ButtonStyle, RoundedRectangleBorder

def upload_button(on_click):
    return ElevatedButton(
        "Upload",
        on_click=on_click,
        width=100,
        height=40,
        style=ButtonStyle(
            bgcolor={"": "#292524"},
            color={"": "white"},
            shape={"": RoundedRectangleBorder(radius=10)},
        ),
    )
