import pandas as pd

# Read the Excel file
file_path = "Meldcodelijst Isolatie - april 2025 (1).xlsx"

# First, get the sheet names
excel_file = pd.ExcelFile(file_path)
print(f"Sheet names: {excel_file.sheet_names}")

# Read the main data sheet (assuming it's called "Meldcodes" like the warmtepomp file)
for sheet_name in excel_file.sheet_names:
    print(f"\n--- Sheet: {sheet_name} ---")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 rows:")
    print(df.head(5))
    
    # For large DataFrames, also print value counts of categorical columns
    if df.shape[0] > 10:
        print("\nValue counts of some columns:")
        for col in df.columns[:5]:  # Look at first few columns
            if df[col].dtype == 'object' or df[col].nunique() < 20:
                print(f"\n{col}:")
                print(df[col].value_counts().head(5)) 