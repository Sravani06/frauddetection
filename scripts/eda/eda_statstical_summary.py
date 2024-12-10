import pandas as pd
import os

#  Set up paths
DATA_PATH = os.path.join(os.getcwd(), 'data', 'Unified_Customer_Policy_Claim_Details.csv')
OUTPUT_DIR = os.path.join(os.getcwd(), 'outputs', 'eda_visualizations')

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(filepath):

    try:
        print(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print("Data loaded successfully!")
        return df
    except FileNotFoundError:
        print(f" File not found at {filepath}. Please check the path and try again.")
        return None


def generate_statistical_summary(df):

    print("\n Generating statistical summary for numerical columns...")

    # Filter only numerical columns
    numerical_columns = df.select_dtypes(include=['int64', 'float64'])

    # Generate descriptive statistics
    summary_statistics = numerical_columns.describe()

    # Save the summary statistics as a CSV
    summary_filepath = os.path.join(OUTPUT_DIR, 'statistical_summary.csv')
    summary_statistics.to_csv(summary_filepath)

    print(f"Statistical summary saved to {summary_filepath}")
    return summary_statistics


if __name__ == "__main__":
    # Load the data
    df = load_data(DATA_PATH)

    if df is not None:
        # Generate the statistical summary
        summary = generate_statistical_summary(df)

        # Display the summary
        print("\n Statistical Summary of Numerical Columns:")
        print(summary)
