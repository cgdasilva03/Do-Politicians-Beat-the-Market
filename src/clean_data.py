import pdfplumber
import pandas as pd
import re
from pathlib import Path

# Set up folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
PDF_FOLDER = PROJECT_DIR / "data" / "raw" / "reports"
OUTPUT_PATH = PROJECT_DIR / "data" / "processed" / "transactions.csv"

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

transactions = []

# Pattern for identifying transaction information
pattern = (
    r"^(.*?)\s+"
    r"([PSXE])(?:\s+\(partial\))?\s+"
    r"(\d{1,2}/\d{1,2}/\d{4})\s+"
    r"(\d{1,2}/\d{1,2}/\d{4})\s+"
    r"(\$[\d,]+)\s*-\s*"
    r"(.*?)\s*"
    r"(\$[\d,]+)(.*)$"
)

owner_codes = ["SP", "JT", "DC"]

# Loop through all downloaded PDF reports
for pdf_path in sorted(PDF_FOLDER.glob("*.pdf")):

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for i, line in enumerate(lines):

                # Only process lines containing two dates
                if len(re.findall(r"\d{1,2}/\d{1,2}/\d{4}", line)) < 2:
                    continue

                combined_line = line

                # Check whether the amount range is complete
                has_complete_amount = re.search(
                    r"\$[\d,]+\s*-\s*.*?\$[\d,]+",
                    line
                )

                # Append the next line if the amount range is incomplete
                if not has_complete_amount and i + 1 < len(lines):
                    combined_line += " " + lines[i + 1]

                match = re.search(pattern, combined_line)

                if not match:
                    continue

                # Extract asset description
                asset_info = match.group(1).strip()
                continuation = match.group(6).strip()

                # Identify owner code
                owner_code = None

                first_word = asset_info.split()[0]

                if first_word in owner_codes:
                    owner_code = first_word
                    asset_info = asset_info[len(first_word):].strip()

                # Combine wrapped asset descriptions
                asset_description = (
                    asset_info + " " + continuation
                ).strip()

                # Create a separate line for metadata extraction
                metadata_line = combined_line

                if i + 1 < len(lines):
                    metadata_line += " " + lines[i + 1]

                # Extract asset type
                asset_type_match = re.search(
                    r"\[(ST|GS)\]",
                    metadata_line
                )

                asset_type = (
                    asset_type_match.group(1)
                    if asset_type_match else None
                )

                # Remove asset type from description
                asset_description = re.sub(
                    r"\[(ST|GS)\]", "", asset_description
                ).strip()

                # Extract ticker
                ticker_match = re.search(
    r"\(([A-Z]{1,5})\)",
    metadata_line
)

                ticker = (
                    ticker_match.group(1)
                    if ticker_match else None
                )

                # Extract CUSIP (9-character security identifier)
                cusip_match = re.search(
                    r"\b([0-9A-Z]{9})\b",
                    asset_description
                )

                cusip = (
                    cusip_match.group(1)
                    if cusip_match else None
                )

                # Extract transaction amounts
                amount_low = int(
                    match.group(5).replace("$", "").replace(",", "")
                )

                amount_high = int(
                    match.group(7).replace("$", "").replace(",", "")
                )

                # Extract dates
                transaction_date = pd.to_datetime(
                    match.group(3), format="%m/%d/%Y"
                )

                disclosure_date = pd.to_datetime(
                    match.group(4), format="%m/%d/%Y"
                )

                # Flag dates that need manual review
                date_check = (
                    "Review"
                    if disclosure_date < transaction_date
                    else "OK"
                )

                # Add transaction to dataset
                transactions.append({
                    "Filing_ID": pdf_path.stem,
                    "Owner_Code": owner_code,
                    "Asset_Description": asset_description,
                    "Asset_Type": asset_type,
                    "Ticker": ticker,
                    "CUSIP": cusip,
                    "Transaction_Type": match.group(2),
                    "Transaction_Date": transaction_date,
                    "Disclosure_Date": disclosure_date,
                    "Amount_Low": amount_low,
                    "Amount_High": amount_high,
                    "Date_Check": date_check
                })


# Convert extracted transactions into a DataFrame
df = pd.DataFrame(transactions)

# Save cleaned transactions
df.to_csv(OUTPUT_PATH, index=False)

print("Successfully extracted transactions!")
# Display transactions that need date review
print("\nTransactions with date issues:")
print(df[df["Date_Check"] == "Review"])

# Display stock transactions missing tickers
print("\nStock transactions missing tickers:")
print(df[
    (df["Asset_Type"] == "ST") &
    (df["Ticker"].isna())
])

# Display transaction counts by asset type
print("\nTransactions by asset type:")
print(df["Asset_Type"].value_counts(dropna=False))

print("\nTransactions extracted per filing:")

filing_counts = (
    df.groupby("Filing_ID")
    .size()
    .sort_values(ascending=False)
)

print(filing_counts)

print("\nNumber of reports processed:", df["Filing_ID"].nunique())

print("\nReports with no extracted transactions:")

downloaded_reports = {
    path.stem
    for path in PDF_FOLDER.glob("*.pdf")
}

processed_reports = set(df["Filing_ID"].unique())

missing_reports = downloaded_reports - processed_reports

print(sorted(missing_reports))
print("Reports without extracted transactions:", len(missing_reports))