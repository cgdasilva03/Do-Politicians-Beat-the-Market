import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Set up file paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

TRANSACTIONS_PATH = (
    PROJECT_DIR / "data" / "processed" / "transactions.csv"
)

XML_PATH = PROJECT_DIR / "data" / "raw" / "2025FD.xml"

OUTPUT_PATH = (
    PROJECT_DIR / "data" / "processed" / "congressional_trades.csv"
)

# --------------------------------------------------
# 2. Load datasets
# --------------------------------------------------

transactions = pd.read_csv(TRANSACTIONS_PATH)
filings = pd.read_xml(XML_PATH)

print("Transactions loaded:", len(transactions))
print("XML filings loaded:", len(filings))

# --------------------------------------------------
# 3. Filter for Periodic Transaction Reports
# --------------------------------------------------

ptr_filings = filings[
    filings["FilingType"].astype(str).str.strip() == "P"
].copy()

print("\nPTR filings:", len(ptr_filings))

# --------------------------------------------------
# 4. Standardize filing IDs
# --------------------------------------------------

transactions["Filing_ID"] = (
    transactions["Filing_ID"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

ptr_filings["DocID"] = (
    ptr_filings["DocID"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
)

# --------------------------------------------------
# 5. Investigate filing ID mismatches
# --------------------------------------------------

transaction_ids = set(transactions["Filing_ID"])
xml_ids = set(ptr_filings["DocID"])

matching_ids = transaction_ids.intersection(xml_ids)

print("\n--- ID COMPARISON ---")

print("Unique transaction IDs:", len(transaction_ids))
print("Unique XML IDs:", len(xml_ids))
print("Matching IDs:", len(matching_ids))

print("\nFirst 20 PTR document IDs:")
print(ptr_filings["DocID"].head(20).tolist())

print("\nPTR document IDs beginning with 200:")
print(
    ptr_filings[
        ptr_filings["DocID"].str.startswith("200")
    ]["DocID"].head(20).tolist()
)

print("\nNumber of PTR IDs beginning with 200:")
print(
    ptr_filings["DocID"].str.startswith("200").sum()
)

print("\nExample transaction ID:")
print(transactions["Filing_ID"].iloc[0])

print("\nDoes that ID exist in the XML?")
print(transactions["Filing_ID"].iloc[0] in xml_ids)

# --------------------------------------------------
# 6. Create politician names
# --------------------------------------------------

ptr_filings["Politician"] = (
    ptr_filings["First"].fillna("") + " " +
    ptr_filings["Last"].fillna("")
).str.strip()

# --------------------------------------------------
# 7. Select filing information
# --------------------------------------------------

filing_info = ptr_filings[
    ["DocID", "Politician", "StateDst", "FilingDate", "Year"]
].copy()

# --------------------------------------------------
# 8. Merge transactions with filing information
# --------------------------------------------------

merged = transactions.merge(
    filing_info,
    left_on="Filing_ID",
    right_on="DocID",
    how="left",
    validate="many_to_one",
    indicator=True
)

# --------------------------------------------------
# 9. Check merge results
# --------------------------------------------------

print("\n--- MERGE RESULTS ---")

print("Total transactions:", len(merged))

print(
    "Successfully matched:",
    (merged["_merge"] == "both").sum()
)

print(
    "Unmatched transactions:",
    (merged["_merge"] == "left_only").sum()
)

# Display unmatched filing IDs
unmatched = merged[
    merged["_merge"] == "left_only"
]

print("\nUnmatched filing IDs:")
print(unmatched["Filing_ID"].unique())

# --------------------------------------------------
# 10. Save merged dataset
# --------------------------------------------------

merged = merged.drop(columns=["DocID", "_merge"])

merged.to_csv(OUTPUT_PATH, index=False)

print("\nMerge process complete!")
print("Saved to:", OUTPUT_PATH)
