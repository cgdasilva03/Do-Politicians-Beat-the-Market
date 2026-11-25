import pandas as pd
import requests
import time
from pathlib import Path

# Set up folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
XML_PATH = PROJECT_DIR / "data" / "raw" / "2025FD.xml"
PDF_FOLDER = PROJECT_DIR / "data" / "raw" / "reports"

PDF_FOLDER.mkdir(parents=True, exist_ok=True)

# Load filing information
df = pd.read_xml(XML_PATH)

# Keep only Periodic Transaction Reports
ptr_df = df[df["FilingType"] == "P"].copy()

print("Total reports to download:", len(ptr_df))

# Track download results
downloaded = 0
skipped = 0
failed = 0

# Create a session
session = requests.Session()

# Download reports
for _, row in ptr_df.iterrows():

    doc_id = row["DocID"]
    year = row["Year"]

    file_path = PDF_FOLDER / f"{doc_id}.pdf"

    # Skip reports already downloaded
    if file_path.exists():
        skipped += 1
        continue

    url = (
        f"https://disclosures-clerk.house.gov/"
        f"public_disc/ptr-pdfs/{year}/{doc_id}.pdf"
    )

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()

        # Verify that the response is a PDF
        if not response.content.startswith(b"%PDF"):
            raise ValueError("Downloaded file is not a valid PDF")

        file_path.write_bytes(response.content)

        downloaded += 1
        print(f"Downloaded: {doc_id}.pdf")

    except (requests.RequestException, ValueError) as e:
        failed += 1
        print(f"Failed: {doc_id}.pdf - {e}")

    # Brief pause between requests
    time.sleep(0.3)

print("\nDownload process complete!")
print("New reports downloaded:", downloaded)
print("Previously downloaded:", skipped)
print("Failed downloads:", failed)
print("Total reports available:", downloaded + skipped)
