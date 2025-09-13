from flet import *
from components.pdf_preview import gerar_preview
from services.repository import PdfRepository
from sqlalchemy.orm import Session
from pathlib import Path
class PdfCard:
    def __init__(
        self,
        page: Page,
        session: Session, # Session,
        caminho_pdf: str,
    ):
        self.page = page
        self.session = session
        self.caminho_pdf = caminho_pdf

        # 1. Busca os dados do PDF no banco de dados
        pdf_repo = PdfRepository(self.session) 
        self.data = pdf_repo.find_one(caminho_pdf)
        if not self.data:
            # Lida com o caso de o PDF não ser encontrado no banco
            self.card_control = Container(content=Text("Erro: PDF não encontrado no banco."), width=220)
            return
            
        # 2. Gera a imagem de preview
        self.preview_image = gerar_preview(self.caminho_pdf, width=210)
        
        # 3. Cria os "chips" de tags para um visual moderno
        tag_chips = []
        # Mostra no máximo 3 tags para não poluir a interface
        for tag_text in self.data.get("tags", [])[:3]:
            tag_chips.append(
                Container(
                    content=Text(tag_text, size=10, color=Colors.BLUE_GREY_800),
                    bgcolor=Colors.BLUE_GREY_100,
                    padding=padding.symmetric(horizontal=8, vertical=4),
                    border_radius=border_radius.all(12)
                )
            )
        
        # 4. Constrói o conteúdo do card
        self.card_content = Container(
            content=Column(
                controls=[
                    self.preview_image,
                    # Título do documento (com quebra de linha elegante)
                    Container(
                        content=Text(
                            self.data["titulo"], 
                            weight=FontWeight.BOLD, 
                            size=14,
                            max_lines=2,
                            overflow=TextOverflow.ELLIPSIS,
                            tooltip=self.data["titulo"] # Mostra o título completo ao passar o mouse
                        ),
                        margin=margin.only(top=10, bottom=5),
                        height=45 # Altura fixa para alinhar os cards
                    ),
                    # Linha com as tags
                    Row(controls=tag_chips, spacing=4)
                ],
                spacing=5,
            ),
            width=220,
            padding=12,
            border_radius=border_radius.all(12),
            bgcolor=Colors.WHITE,
            border=border.all(1, Colors.GREY_300),
            # Sombra sutil para um efeito de elevação
            shadow=BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=Colors.with_opacity(0.1, Colors.BLACK),
                offset=Offset(0, 2),
            ),
            # Animação suave para a sombra e escala no hover
            animate=Animation(200, "easeOut"),
            animate_scale=True,
        )
        
        # 5. Torna o card clicável e adiciona efeito de hover
        self.clickable_area = GestureDetector(
            content=self.card_content,
            on_tap=self.ir_pdf_view,
            # on_click=self.ir_pdf_view,
            on_hover=self._handle_hover,
            mouse_cursor=MouseCursor.CLICK,
        )

    def ir_pdf_view(self, e):
        pdf_id = self.data["id"]
        self.page.go(f"/pdf/{pdf_id}")
    def _handle_hover(self, e: HoverEvent):
        """Aplica um efeito visual ao passar o mouse."""
        self.card_content.shadow.blur_radius = 15 if e.data == "true" else 5
        self.card_content.scale = 1.03 if e.data == "true" else 1.0
        self.page.update()

    def build(self) -> GestureDetector:
        """Retorna o controle Flet final e pronto para ser adicionado à página."""
        # Se o card não foi criado por um erro, retorna o controle de erro
        if not hasattr(self, 'clickable_area'):
            return self.card_control
        return self.clickable_area
