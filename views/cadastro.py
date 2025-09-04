from flet import *
from components.buttons import btn_padrao
from services.database import get_options_turma
from services.arquivos import salvar_arquivo_temp, get_data_pdf, salvar_arquivo
from components.pdf_preview import gerar_preview
def cadastro_view(page):
    page.snack_bar = SnackBar(Text(""))
    arquivo_selecionado = None
    caminho = None
    def on_file_selected(e: FilePickerResultEvent):
        nonlocal arquivo_selecionado
        arquivo_selecionado = e
        caminho = salvar_arquivo_temp(e, page)
        res = get_data_pdf(caminho)
        # print(res)
        put_textfield(res)

    def on_save_button():
        if (arquivo_selecionado != None):
            salvar_arquivo(arquivo_selecionado, page)
        
    
    # cria o file_picker
    file_picker = FilePicker(on_result=on_file_selected)

    # adiciona ao overlay da página
    page.overlay.append(file_picker)

    pdf_preview = Container(
        content=Text("Preview do PDF selecionado", size=16, weight="bold"),
        alignment=alignment.center,
        bgcolor="#f4f4f5",
        border_radius=10,
        width=250,
        height=250 * 1.414,
    )
    upload_btn = btn_padrao("Upload",lambda _: file_picker.pick_files())
    col_esquerda = Column(controls=[pdf_preview, upload_btn], alignment="center")
    
    # Elementos coluna direita
    turmas = get_options_turma()
    lista_opcoes = [dropdown.Option(turma.nome) for turma in turmas]
    drop_down = Dropdown(
        label="Escolha uma turma (opcional)",
        options=lista_opcoes,
        width=300
    )
    btn_salvar = btn_padrao("Salvar", lambda _: on_save_button())
    btn_cancelar = btn_padrao("Cancelar", None)
    btn_cancelar.bgcolor = "#f3f3f3"
    btn_cancelar.color = "#000000"
    tf_titulo = TextField(label="Título do Documento", expand=True)
    tf_tags = TextField(label="Tags (separe por vírgula)", expand=True)
    text_fields = Container(
        content=Column(
            controls=[
                Text("Título:", weight="bold", size=20),
                tf_titulo,
                Text("Tags:", weight="bold",size=20),
                tf_tags,
                Text("Turma:", weight="bold",size=20),
                Row(controls=[drop_down, btn_cancelar, btn_salvar])
            ]
        ),
        height=300,
        padding=padding.only(left=20),
        
    )
    titulo_col_direita = Text("Cadastrar PDF", size=40, weight="bold")
    col_direita = Column(
        controls=[
            titulo_col_direita,
            text_fields
        ],
        spacing=20,
        expand=True,
        alignment="center"
    )
    def put_textfield(conteudo):
        try:
            tf_titulo.value = conteudo["titulo"]
            tags = conteudo["tags"]
            # garantir que todos são strings
            tags_string = ", ".join(str(t) for t in tags)
            tf_tags.value = tags_string
            col_esquerda.controls.clear()
            col_esquerda.controls.append(gerar_preview(conteudo["caminho"]))
            page.update()
        except Exception as e:
            print("Erro em put_textfield:", e)

        
    return View(
        route="/cadastro",
        controls=[Row(controls=[col_esquerda, col_direita], expand=True, spacing=40)],
        padding=padding.all(40),
    )


