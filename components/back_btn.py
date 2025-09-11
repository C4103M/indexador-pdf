from flet import *
from sqlalchemy.orm import Session

class BackButton:
    def __init__(self, page: Page, session: Session):
        self.page = page
        self.session = session
        self.botao = IconButton(icon=Icons.ARROW_BACK, on_click=lambda _: self.go_back())

    def go_back(self):
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.go(self.page.views[-1].route)
        else:
            # Caso não tenha view anterior, volta para "/"
            self.page.go("/")

    def build(self) -> IconButton:
        return self.botao