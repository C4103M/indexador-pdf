from flet import *
from views.home import home_view
from views.cadastro import cadastro_view
from views.lista_pdfs import list_view
from views.config import config_view
from views.pdf_expand import pdf_expand_view
from views.pdf_edit import edit_view
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.repository import PdfRepository
from services.models import Base



def main(page: Page):
    engine = create_engine("sqlite:///pdfs.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine) # Cria as tabelas se não existirem
    # Cria uma nova sessão para consultas
    Session = sessionmaker(bind=engine)
    session = Session()
    # Inicializar o repositório (classe) pdf, para consultas e inserções
    pdf_repo = PdfRepository(session)
    # page.theme_mode = ThemeMode.LIGHT
    # ss = Session()
    # print(PdfRepository(ss).find_all())
    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page, session))
        elif page.route == "/cadastro":
            page.views.append(cadastro_view(page, session))
        elif page.route == "/config":
            page.views.append(config_view(page, session))
        elif page.route == "/listar":
            page.views.append(list_view(page, session))
        elif page.route.startswith("/pdf/"):
            pdf_id = int(page.route.split("/")[-1])  # extrai o ID da rota
            page.views.append(pdf_expand_view(page, session, pdf_id))
        elif page.route.startswith("/edit/"):
            pdf_id = int(page.route.split("/")[-1])  # extrai o ID da rota
            page.views.append(edit_view(page, session, pdf_id))
        page.update()

    page.on_route_change = route_change
    page.go("/")

app(target=main)