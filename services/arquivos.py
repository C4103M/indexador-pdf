import os
import shutil
from flet import FilePickerResultEvent, SnackBar, Text

def salvar_arquivo_temp(e: FilePickerResultEvent, page):
    if not e.files:  # caso o usuário cancele a seleção
        return
    
    f = e.files[0]  # pega apenas o primeiro arquivo
    origem = f.path
    destino_dir = "pdfs/temp"
    os.makedirs(destino_dir, exist_ok=True)  # cria pasta se não existir
    destino = os.path.join(destino_dir, f.name)

    shutil.copy(origem, destino)

    # feedback visual
    page.snack_bar = SnackBar(Text(f"Arquivo salvo em {destino}"))
    page.snack_bar.open = True
    page.update()
    
    return destino

def get_data_pdf(caminho):
    return