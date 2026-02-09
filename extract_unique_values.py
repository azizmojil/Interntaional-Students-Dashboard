import pandas as pd
import os

def extract_unique_values():
    file_path = os.path.join('data', 'data.xlsx')
    output_file = 'unique_values.txt'
    columns_to_extract = [
        'LAST_STST', 'CELG_CODE', 'LAST_TERM',
        'CITZ_DESC', 'MAJR_DESC', 'COLL_DESC'
    ]

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        # explicit engine='openpyxl' is often safer for xlsx if installed
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Description at the very top
            f.write("DATA DESCRIPTION REPORT\n")
            f.write("=======================\n")
            f.write(f"Source File: {file_path}\n")
            f.write("Content: Unique values for columns LAST_STST, CELG_CODE, LAST_TERM, CITZ_DESC, MAJR_DESC, COLL_DESC.\n")
            f.write("This file contains a list of all unique entries found in the specified columns to assist with data analysis and filtering.\n\n")

            for col in columns_to_extract:
                f.write(f"COLUMN: {col}\n")
                if col in df.columns:
                    unique_vals = df[col].dropna().unique()
                    f.write(f"Count: {len(unique_vals)} unique values\n")
                    f.write("-" * 30 + "\n")
                    # Sort values for better readability, converting to string to handle mixed types safely
                    for val in sorted(unique_vals, key=lambda x: str(x)):
                        f.write(f"{val}\n")
                else:
                    f.write("WARNING: Column not found in the dataset.\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
        
        print(f"Successfully created {output_file}")

    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    extract_unique_values()
