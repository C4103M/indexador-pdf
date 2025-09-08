from flet import (
    Container,
    Row,
    Image,
    Text,
    Column,
    MainAxisAlignment,
    padding,
    Page,
    GestureDetector,
)


class SideBar:
    def __init__(self, page: Page):
        self.page = page
        self.home = GestureDetector(
            content=Container(
                content=Row(
                    controls=[
                        Image("./elements/home.png", width=20, height=20),
                        Text("Home", weight="bold"),
                    ],
                    alignment=MainAxisAlignment.START,
                ),
                width=250,
                height=30,
                padding=padding.only(left=5),
            ),
            on_tap=self.ir_para_home,
        )
        self.arquivos = GestureDetector(
            content=Container(
                content=Row(
                    controls=[
                        Image("./elements/pasta.png", width=20, height=20),
                        Text("Arquivos", weight="bold"),
                    ],
                    alignment=MainAxisAlignment.START,
                ),
                width=250,
                height=40,
                padding=padding.only(left=5),
            ),
            on_tap=self.ir_para_cadastro,
        )
        self.configuracoes = GestureDetector(
            content=Container(
                content=Row(
                    controls=[
                        Image("./elements/config.png", width=20, height=20),
                        Text("Configurações", weight="bold"),
                    ],
                    alignment=MainAxisAlignment.START,
                ),
                width=250,
                height=40,
                padding=padding.only(left=5),
            ),
            on_tap=self.ir_para_config,
        )

    def build(self) -> Column:
        return Column(
            controls=[self.home, self.arquivos, self.configuracoes], width=250
        )

    # Funções de redirecionamento
    def ir_para_cadastro(self, e):
        """Função que redireciona o usuário para a rota /cadastro."""
        print("Redirecionando para /lista...")
        self.page.go("/listar")

    def ir_para_home(self, e):
        """Função que redireciona o usuário para a rota inicial."""
        print("Redirecionando para /...")
        self.page.go("/")

    def ir_para_config(self, e):
        """Função que redireciona o usuário para a página de configuração."""
        print("Redirecionando para /config...")
        self.page.go("/config")


def sidebar(page: Page):
    return SideBar(page).build()
