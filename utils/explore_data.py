import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def explore_excel_file(file_path):
    """Explore and display information about the Excel file"""
    print(f"Exploring file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path)} bytes")
    
    # Read using ExcelFile to get sheet names
    try:
        excel_file = pd.ExcelFile(file_path)
        print(f"\nSheet names: {excel_file.sheet_names}")
        
        sheets_data = {}
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            
            # Try different approaches to read the sheet
            # First try with no parameters
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Shape with no parameters: {df.shape}")
            print("First 5 rows:")
            print(df.head(5))
            
            # Try with skiprows parameter
            for skip_rows in [1, 5, 10]:
                try:
                    df_skip = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
                    print(f"\nShape with skiprows={skip_rows}: {df_skip.shape}")
                    if not df_skip.empty:
                        print("Columns:", list(df_skip.columns))
                        print("First 3 rows:")
                        print(df_skip.head(3))
                except Exception as e:
                    print(f"Error reading with skiprows={skip_rows}: {e}")
            
            # Store the data
            sheets_data[sheet_name] = df
        
        return sheets_data
    
    except Exception as e:
        print(f"Error exploring file: {e}")
        return None

if __name__ == "__main__":
    file_path = "data/Meldcodelijst Warmtepompen - april 2025 (3).xlsx"
    data = explore_excel_file(file_path) 