import pandas as pd
from pathlib import Path

# Set up file paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_DIR / "data" / "processed" / "congressional_trades.csv"
)

OUTPUT_PATH = (
    PROJECT_DIR / "data" / "processed" / "stock_purchases.csv"
)

# Load merged dataset
df = pd.read_csv(INPUT_PATH)

print("Original transactions:", len(df))

# Keep stock purchases only
stocks = df[
    (df["Asset_Type"] == "ST") &
    (df["Transaction_Type"] == "P")
].copy()

print("Stock purchases:", len(stocks))

# Remove transactions without tickers
stocks = stocks.dropna(subset=["Ticker"])

# Remove blank tickers
stocks["Ticker"] = stocks["Ticker"].astype(str).str.strip()
stocks = stocks[stocks["Ticker"] != ""]

# Convert dates
stocks["Transaction_Date"] = pd.to_datetime(
    stocks["Transaction_Date"],
    errors="coerce"
)

stocks["Disclosure_Date"] = pd.to_datetime(
    stocks["Disclosure_Date"],
    errors="coerce"
)

# Remove rows with invalid transaction dates
stocks = stocks.dropna(subset=["Transaction_Date"])

# Sort by transaction date
stocks = stocks.sort_values("Transaction_Date")

# Save prepared dataset
stocks.to_csv(OUTPUT_PATH, index=False)

print("\nData preparation complete!")
print("Final stock purchases:", len(stocks))
print("Unique tickers:", stocks["Ticker"].nunique())
print("Saved to:", OUTPUT_PATH)

print("\nSample:")
print(stocks.head())
