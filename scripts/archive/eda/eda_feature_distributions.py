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
        print(f" Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print("Data loaded successfully!")
        return df
    except FileNotFoundError:
        print(f" File not found at {filepath}. Please check the path and try again.")
        return None


def visualize_distribution_of_numerical_features(df):
    """
    Visualize the distribution of key numerical features.
    """
    numerical_features = ['CLM_AMT', 'DAYS_BETWEEN_OCCUR_AND_REPORT']

    for feature in numerical_features:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[feature], kde=True, color='skyblue')
        plt.title(f"Distribution of {feature}")
        plt.xlabel(feature)
        plt.ylabel("Frequency")

        # Save plot
        plot_filepath = os.path.join(OUTPUT_DIR, f'distribution_{feature}.png')
        plt.savefig(plot_filepath)
        print(f"Distribution plot for {feature} saved to {plot_filepath}")
        plt.show()


def visualize_categorical_feature_distribution(df):
    """
    Visualize the distribution of key categorical features.
    """
    categorical_features = ['INJURY_SEVERITY', 'CLM_OCCR_STATE', 'RISK_LEVEL']

    for feature in categorical_features:
        plt.figure(figsize=(10, 6))
        sns.countplot(x=feature, data=df, order=df[feature].value_counts().index, palette='Set2')
        plt.title(f"Distribution of {feature}")
        plt.xlabel(feature)
        plt.ylabel("Count")

        # Save plot
        plot_filepath = os.path.join(OUTPUT_DIR, f'distribution_{feature}.png')
        plt.savefig(plot_filepath)
        print(f" Categorical distribution plot for {feature} saved to {plot_filepath}")
        plt.show()


def visualize_fraud_vs_non_fraud(df, feature):
    """
    Visualize the feature distribution for fraud vs non-fraud.
    """
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='CLM_FRAUD_IND', y=feature, data=df, palette='Set2')
    plt.title(f"Fraud vs. Non-Fraud for {feature}")
    plt.xlabel("Fraud Indicator (0 = Non-Fraud, 1 = Fraud)")
    plt.ylabel(feature)

    # Save plot
    plot_filepath = os.path.join(OUTPUT_DIR, f'fraud_vs_{feature}.png')
    plt.savefig(plot_filepath)
    print(f"Fraud vs. Non-Fraud plot for {feature} saved to {plot_filepath}")
    plt.show()


if __name__ == "__main__":
    # Load the data
    df = load_data(DATA_PATH)

    if df is not None:
        # Step 1: Visualize distributions of numerical features
        visualize_distribution_of_numerical_features(df)

        # Step 2: Visualize distributions of categorical features
        visualize_categorical_feature_distribution(df)

        # Step 3: Visualize fraud vs non-fraud distribution for key features
        for feature in ['CLM_AMT', 'DAYS_BETWEEN_OCCUR_AND_REPORT']:
            visualize_fraud_vs_non_fraud(df, feature)
