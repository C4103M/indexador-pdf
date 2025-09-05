from flet import *
from sqlalchemy.orm import Session

class ConfigView:
    def __init__(self, page: Page, session: Session):
        pass
    def build(self) -> View:
        return View(
            route="/cadastro",
            controls=[
            ],
            padding=padding.all(40),
        )
    
    
def config_view(page: Page, session: Session):
    ConfigView(page, session).build()
    