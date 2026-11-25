import pdfplumber
from pathlib import Path
import re

# Locate the reports folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
PDF_FOLDER = PROJECT_DIR / "data" / "raw" / "reports"

# Select the first PDF
pdf_files = list(PDF_FOLDER.glob("*.pdf"))
pdf_path = pdf_files[0]

# Pattern for dates
date_pattern = r"\d{2}/\d{2}/\d{4}"

with pdfplumber.open(pdf_path) as pdf:

    for page in pdf.pages:

        text = page.extract_text()

        if text:
            lines = text.split("\n")

            for line in lines:

                if len(re.findall(date_pattern, line)) >= 2:
                    print(line)
