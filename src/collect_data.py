import pandas as pd
from pathlib import Path

# Set up project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
XML_PATH = PROJECT_DIR / "data" / "raw" / "2025FD.xml"
OUTPUT_PATH = PROJECT_DIR / "data" / "processed" / "ptr_filings.csv"

# Create processed folder if it doesn't exist
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Load the congressional filing index
df = pd.read_xml(XML_PATH)

# Keep only Periodic Transaction Reports
ptr_df = df[df["FilingType"] == "P"].copy()

# Create a full politician name
ptr_df["Politician"] = (
    ptr_df["First"].fillna("") + " " +
    ptr_df["Last"].fillna("")
).str.strip()

# Save the PTR filing information
ptr_df.to_csv(OUTPUT_PATH, index=False)

# Display results
print("Successfully collected congressional filing information")
print("Total PTR filings:", len(ptr_df))
print("Saved to:", OUTPUT_PATH)
