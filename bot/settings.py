from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
STATIC = os.path.join(BASE_DIR, "static/")
images_path = os.path.join(STATIC, "images/")
csv_path = os.path.join(STATIC, "csv/")

CSV_DELIMITER = "#"
