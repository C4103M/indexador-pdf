from flet import *
from views.home import home_view
from views.cadastro import cadastro_view

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.repository import PdfRepository
from services.models import Base

engine = create_engine("sqlite:///pdfs.db")
Base.metadata.create_all(bind=engine) # Cria as tabelas se não existirem
# Cria uma nova sessão para consultas
Session = sessionmaker(bind=engine)
session = Session()
# Inicializar o repositório (classe) pdf, para consultas e inserções
pdf_repo = PdfRepository(session)


def main(page: Page):
    page.theme_mode = ThemeMode.LIGHT

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page, session))
        elif page.route == "/cadastro":
            page.views.append(cadastro_view(page, session))
        elif page.route == "/config":
            page.views.append(cadastro_view(page, session))
        page.update()

    page.on_route_change = route_change
    page.go("/")

app(target=main)