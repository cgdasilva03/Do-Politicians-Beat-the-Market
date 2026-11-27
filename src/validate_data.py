import pandas as pd
from pathlib import Path

# Set up file paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR / "data" / "processed" / "congressional_trades.csv"
)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Basic dataset information
print("Total transactions:", len(df))
print("Total columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Count transactions by asset type
print("\nTransactions by asset type:")
print(df["Asset_Type"].value_counts(dropna=False))

# Count transactions by transaction type
print("\nTransactions by transaction type:")
print(df["Transaction_Type"].value_counts(dropna=False))

# Count transactions by politician
print("\nTop 10 politicians by transaction count:")
print(df["Politician"].value_counts().head(10))

# Check date ranges
df["Transaction_Date"] = pd.to_datetime(
    df["Transaction_Date"],
    errors="coerce"
)

df["Disclosure_Date"] = pd.to_datetime(
    df["Disclosure_Date"],
    errors="coerce"
)

print("\nTransaction date range:")
print(df["Transaction_Date"].min(), "to", df["Transaction_Date"].max())

print("\nDisclosure date range:")
print(df["Disclosure_Date"].min(), "to", df["Disclosure_Date"].max())
