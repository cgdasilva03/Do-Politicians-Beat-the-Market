import pandas as pd
import requests
from pathlib import Path

# Set up project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
XML_PATH = PROJECT_DIR / "data" / "raw" / "2025FD.xml"
PDF_FOLDER = PROJECT_DIR / "data" / "raw" / "reports"

# Create folder if it doesn't exist
PDF_FOLDER.mkdir(parents=True, exist_ok=True)

# Load filing index
df = pd.read_xml(XML_PATH)

# Keep only PTR filings
ptr_df = df[df["FilingType"] == "P"].copy()

# Download the first five reports
sample = ptr_df.head(5)

for _, row in sample.iterrows():

    doc_id = row["DocID"]
    year = row["Year"]

    url = (
        f"https://disclosures-clerk.house.gov/"
        f"public_disc/ptr-pdfs/{year}/{doc_id}.pdf"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    file_path = PDF_FOLDER / f"{doc_id}.pdf"
    file_path.write_bytes(response.content)

    print(f"Downloaded: {doc_id}.pdf")

print("\nFinished downloading sample reports!")