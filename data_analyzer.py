import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)

def analyze_excel():
    excel_file = 'dataset.xlsx'
    sheets = pd.read_excel(excel_file, sheet_name=None)
    
    print("\n=== Excel Sheet Analysis ===")
    for sheet_name, df in sheets.items():
        print(f"\nSheet: {sheet_name}")
        print("Columns:", list(df.columns))
        print("\nFirst few rows:")
        print(df.head())

if __name__ == "__main__":
    analyze_excel() 