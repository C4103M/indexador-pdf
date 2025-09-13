from flet import * 
from sqlalchemy.orm import Session
from services.repository import AgrupamentoRepository
from components.back_btn import BackButton
import os
import json

class ConfigView:
    def __init__(self, page: Page, session: Session):
        self.page = page
        self.session = session
        self.repo = AgrupamentoRepository(self.session)
        
        # --- Controles da UI ---

        # Seção de Adicionar Agrupamento
        self.txt_novo_agrupamento = TextField(
            label="Nome do novo agrupamento",
            expand=True,
            on_submit=self._adicionar_agrupamento
        )
        
        # Seção de Remover Agrupamento
        self.dropdown_agrupamentos = Dropdown(
            label="Selecione um agrupamento para remover",
            expand=True,
            on_change=self._atualizar_estado_botao_remover
        )
        self.btn_remover = IconButton(
            icon=Icons.DELETE_FOREVER,
            icon_color=Colors.RED_400,
            tooltip="Remover agrupamento selecionado",
            on_click=self._remover_agrupamento,
            disabled=True # Começa desabilitado
        )
        
        # Carrega os dados iniciais
        self._carregar_agrupamentos()

        self.voltar = BackButton(self.page, self.session)
        self.voltar = self.voltar.build()

    def _carregar_agrupamentos(self):
        """Busca os agrupamentos do banco e atualiza o dropdown."""
        agrupamentos = self.repo.find_all()
        self.dropdown_agrupamentos.options.clear()
        for agrupamento in agrupamentos:
            self.dropdown_agrupamentos.options.append(
                dropdown.Option(agrupamento.nome)
            )
        self._atualizar_estado_botao_remover(None)
        self.page.update()

    def _adicionar_agrupamento(self, e):
        """Adiciona um novo agrupamento ao banco de dados."""
        nome_novo_agrupamento = self.txt_novo_agrupamento.value.strip()
        if not nome_novo_agrupamento:
            self.page.open(SnackBar(Text("O nome do agrupamento não pode estar vazio.")))
            return
        try:
            # Verifica se já existe
            if self.repo.find_by_name(nome_novo_agrupamento):
                 self.page.open(SnackBar(Text(f"O agrupamento '{nome_novo_agrupamento}' já existe."), open=True))
                 return
            self.repo.create(nome_novo_agrupamento)
            self.session.commit()
            
            self.txt_novo_agrupamento.value = ""
            self._carregar_agrupamentos() # Atualiza a lista
            self.page.open(SnackBar(Text(f"Agrupamento '{nome_novo_agrupamento}' adicionado com sucesso!")))
        except Exception as ex:
            self.page.open(SnackBar(Text(f"Erro ao adicionar agrupamento: {ex}"), open=True))
            self.session.rollback()

    def _remover_agrupamento(self, e):
        """Remove o agrupamento selecionado do banco de dados."""
        nome_selecionado = self.dropdown_agrupamentos.value
        if not nome_selecionado:
            return

        try:
            agrupamento_para_remover = self.repo.find_by_name(nome_selecionado)
            if agrupamento_para_remover:
                self.repo.delete(nome_selecionado)
                self._carregar_agrupamentos() # Atualiza a lista
                self.page.open(SnackBar(Text(f"Agrupamento '{nome_selecionado}' removido com sucesso!"), open=True))
        except Exception as ex:
            self.page.open(SnackBar(Text(f"Erro ao remover agrupamento: {ex}"), open=True))
            self.session.rollback()
            
    def _atualizar_estado_botao_remover(self, e):
        """Habilita ou desabilita o botão de remover."""
        self.btn_remover.disabled = self.dropdown_agrupamentos.value is None
        self.page.update()
        
    def _on_directory_selected(self, e: FilePickerResultEvent):
        """Atualiza o texto com o caminho da pasta selecionada e salva em settings.json."""
        if e.path:
            self.txt_caminho_salvar.value = e.path
            self.txt_caminho_salvar.italic = False

            # Caminho do settings.json (mesma pasta onde está o script principal)
            settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")

            # Salva o caminho no JSON
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump({"path_default": e.path}, f, indent=4, ensure_ascii=False)

        else:
            self.txt_caminho_salvar.value = "Nenhum local selecionado."
            self.txt_caminho_salvar.italic = True

        self.page.update()

    def build(self) -> View:
        return View(
            route="/config",
            appbar=AppBar(
                leading=self.voltar,
                title=Text("Gerenciar Agrupamentos de arquivos", size=20, weight=FontWeight.BOLD),
            ),
            controls=[
                Column(
                    [
                        Card(
                            content=Container(
                                Column([
                                    Text("Adicionar Novo Agrupamento", weight=FontWeight.BOLD),
                                    Row([self.txt_novo_agrupamento, IconButton(icon=Icons.ADD, on_click=self._adicionar_agrupamento, tooltip="Adicionar")]),
                                    Divider(),
                                    Text("Remover Agrupamento Existente", weight=FontWeight.BOLD),
                                    Row([self.dropdown_agrupamentos, self.btn_remover]),
                                ]),
                                padding=20
                            )
                        ),
                    ],
                    spacing=20
                )
            ],
            padding=padding.all(20),
        )

# Função "fábrica" para ser usada no seu roteador principal
def config_view(page: Page, session: Session):
    return ConfigView(page, session).build()
