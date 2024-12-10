import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Step 1: Set up paths
DATA_PATH = os.path.join(os.getcwd(), 'data', 'Unified_Customer_Policy_Claim_Details.csv')
OUTPUT_DIR = os.path.join(os.getcwd(), 'outputs', 'eda_visualizations')

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data(filepath):
    """
    Load the dataset from the given filepath.
    """
    try:
        print(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print("Data loaded successfully!")
        return df
    except FileNotFoundError:
        print(f"File not found at {filepath}. Please check the path and try again.")
        return None

def check_class_imbalance(df):
    """
    Check for class imbalance of the CLM_FRAUD_IND column.
    """
    print("\n Checking for class imbalance in CLM_FRAUD_IND...")

    # Count and percentage of fraud vs. non-fraud claims
    fraud_counts = df['CLM_FRAUD_IND'].value_counts()
    fraud_percentage = df['CLM_FRAUD_IND'].value_counts(normalize=True) * 100

    print("\n Fraud Count and Percentage:")
    print(fraud_counts)
    print(fraud_percentage)

    return fraud_counts, fraud_percentage

def visualize_class_imbalance(fraud_counts):
    """
    Create and save a bar plot to visualize the class imbalance.
    """
    print("\n Visualizing class imbalance...")

    # Create a bar plot
    plt.figure(figsize=(8, 6))
    sns.barplot(x=fraud_counts.index, y=fraud_counts.values, palette=['green', 'red'])

    # Set plot details
    plt.title("Fraud vs. Non-Fraud Claims")
    plt.xlabel("Fraud Indicator (0 = Non-Fraud, 1 = Fraud)")
    plt.ylabel("Count")
    plt.xticks(ticks=[0, 1], labels=['Non-Fraud', 'Fraud'])

    # Save the plot
    plot_filepath = os.path.join(OUTPUT_DIR, 'class_imbalance.png')
    plt.savefig(plot_filepath)
    print(f" Class imbalance plot saved to {plot_filepath}")

    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Load the data
    df = load_data(DATA_PATH)

    if df is not None:
        # Step 1: Check class imbalance
        fraud_counts, fraud_percentage = check_class_imbalance(df)

        # Step 2: Visualize class imbalance
        visualize_class_imbalance(fraud_counts)
