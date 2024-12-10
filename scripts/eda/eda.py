import os
import pandas as pd

# Set the path to the data file
DATA_PATH = os.path.join(os.getcwd(), 'data', 'Unified_Customer_Policy_Claim_Details.csv')

def load_data(filepath):
    """
    Load the dataset from the given filepath.
    """
    try:
        print(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print("✅ Data loaded successfully!")
        return df
    except FileNotFoundError:
        print(f"❌ File not found at {filepath}. Please check the path and try again.")
        return None

if __name__ == "__main__":
    # Load the unified dataset
    df = load_data(DATA_PATH)

    # Display basic information about the dataset
    if df is not None:
        print("\nData Summary:")
        print(df.info())
        print("\nPreview of the Data:")
        print(df.head())
