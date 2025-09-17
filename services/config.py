# config.py
from pathlib import Path
from appdirs import user_data_dir

standard_dir = Path(user_data_dir("IndexadorPDFs"))
dir_pdfs = Path(user_data_dir("IndexadorPDFs")) / "pdfs"
dir_temp = dir_pdfs / "temp"

standard_dir.mkdir(parents=True, exist_ok=True)
dir_pdfs.mkdir(parents=True, exist_ok=True)
dir_temp.mkdir(parents=True, exist_ok=True)