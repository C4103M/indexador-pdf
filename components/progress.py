from flet import *
import time
import threading

class LoadingOverlay:
    def __init__(self, page: Page):
        self.page = page
        self.total = 250

        # Usando 'Colors' (maiúsculo) para constantes
        self.barra = Container(
            width=self.total, height=12, bgcolor=Colors.BLACK12, border_radius=border_radius.all(6)
        )
        self.preenchimento = Container(
            width=0,
            height=12,
            bgcolor=Colors.BLUE_600, # <-- CORRIGIDO
            border_radius=border_radius.all(6),
            animate=Animation(300, "easeOut"),
        )
        
        # Usando 'colors' (minúsculo) para a função with_opacity
        self.overlay = Container(
            content=Stack([self.barra, self.preenchimento]),
            expand=True,
            bgcolor=Colors.with_opacity(0.4, Colors.WHITE), # <-- CORRETO (função)
            blur=Blur(12, 12, BlurTileMode.CLAMP),
            alignment=alignment.center,
            visible=False,
        )

    # ... (O resto da classe não precisa de alterações) ...
    def build(self):
        return self.overlay

    def show(self):
        self.overlay.visible = True
        self.page.update()

    def hide(self):
        self.overlay.visible = False
        self.page.update()

    def set_progress(self, porcentagem: float):
        porcentagem = max(0.0, min(1.0, porcentagem))
        self.preenchimento.width = self.total * porcentagem
        self.page.update()


# def main(page: Page):
#     page.title = "Overlay e Animação Corretos"
#     page.horizontal_alignment = CrossAxisAlignment.CENTER
#     page.vertical_alignment = MainAxisAlignment.CENTER

#     overlay = LoadingOverlay(page)
#     page.overlay.append(overlay.build())

#     def processo_em_background():
#         page.run_thread(overlay.show)
#         for i in range(11):
#             percentual = i / 10
#             page.run_thread(overlay.set_progress, percentual)
#             time.sleep(0.2)
#         page.run_thread(overlay.hide)

#     def iniciar_loading(e):
#         thread = threading.Thread(target=processo_em_background, daemon=True)
#         thread.start()

#     page.add(ElevatedButton("Iniciar Loading", on_click=iniciar_loading, height=50))
#     page.update()

# app(target=main)