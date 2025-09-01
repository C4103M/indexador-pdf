from flet import *
from views.home import home_view
from views.cadastro import cadastro_view

def main(page: Page):
    page.theme_mode = ThemeMode.LIGHT

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page))
        elif page.route == "/cadastro":
            page.views.append(cadastro_view(page))
        page.update()

    page.on_route_change = route_change
    page.go("/")

app(target=main)