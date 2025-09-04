import fitz  # PyMuPDF
import io
import base64
from flet import Image, Column

def gerar_preview(caminho_pdf: str, width=250) -> Image:
    import fitz, base64

    try:
        pdf = fitz.open(caminho_pdf)
        pagina = pdf[0]

        # escalonamento proporcional
        zoom = width / pagina.rect.width
        mat = fitz.Matrix(zoom, zoom)
        pix = pagina.get_pixmap(matrix=mat, alpha=False)  # desativa transparência para economizar bytes

        img_bytes = pix.tobytes("png")
        src_b64 = base64.b64encode(img_bytes).decode()
    except Exception as e:
        print("Erro ao gerar preview:", e)
        src_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIW2P8z/C/HwAF/gL+J6gk/gAAAABJRU5ErkJggg=="

    return Image(src_base64=src_b64, width=width)
