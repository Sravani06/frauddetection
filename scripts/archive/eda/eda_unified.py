import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set paths
DATA_PATH = os.path.join(os.getcwd(), 'data', 'Unified_Customer_Policy_Claim_Details.csv')
OUTPUT_DIR = os.path.join(os.getcwd(), 'outputs', 'eda_analysis')

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(filepath):
    """Load the dataset from the given filepath."""
    try:
        print(f" Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print("Data loaded successfully!")
        return df
    except FileNotFoundError:
        print(f" File not found at {filepath}. Please check the path and try again.")
        return None


def correlation_analysis(df):
    """Perform correlation analysis and visualize the results."""
    print(" Performing correlation analysis...")
    numerical_features = df.select_dtypes(include=['float64', 'int64']).columns

    # Correlation matrix
    corr_matrix = df[numerical_features].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title("Correlation Matrix")
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_matrix.png'))
    print(" Correlation matrix saved.")
    plt.show()


def outlier_detection(df):
    """Visualize outliers for key numerical features."""
    print(" Detecting outliers...")
    numerical_features = ['CLM_AMT', 'DAYS_BETWEEN_OCCUR_AND_REPORT']

    for feature in numerical_features:
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=df[feature], color='skyblue')
        plt.title(f"Outlier Detection: {feature}")
        plt.savefig(os.path.join(OUTPUT_DIR, f'outlier_{feature}.png'))
        print(f" Outlier detection plot for {feature} saved.")
        plt.show()


def temporal_analysis(df):
    """Analyze fraud trends over time."""
    print(" Performing temporal analysis...")
    df['CLM_RPT_DT'] = pd.to_datetime(df['CLM_RPT_DT'])
    fraud_trend = df.groupby(df['CLM_RPT_DT'].dt.to_period('M'))['CLM_FRAUD_IND'].mean()

    plt.figure(figsize=(12, 6))
    fraud_trend.plot(kind='line', marker='o', color='red')
    plt.title("Fraud Rate Over Time")
    plt.xlabel("Report Date (Monthly)")
    plt.ylabel("Fraud Rate")
    plt.grid()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fraud_trend_over_time.png'))
    print("Fraud trend analysis saved.")
    plt.show()


def state_level_fraud_analysis(df):
    """Analyze fraud rates by state."""
    print("Analyzing fraud by state...")
    state_fraud_rate = df.groupby('CLM_OCCR_STATE')['CLM_FRAUD_IND'].mean().sort_values(ascending=False)

    plt.figure(figsize=(12, 6))
    state_fraud_rate.plot(kind='bar', color='purple')
    plt.title("Fraud Rate by State")
    plt.xlabel("State")
    plt.ylabel("Fraud Rate")
    plt.savefig(os.path.join(OUTPUT_DIR, 'fraud_rate_by_state.png'))
    print("State-level fraud analysis saved.")
    plt.show()


def cross_feature_analysis(df):
    """Perform cross-feature analysis."""
    print(" Performing cross-feature analysis...")
    pivot_table = pd.pivot_table(
        df, values='CLM_FRAUD_IND',
        index='INJURY_SEVERITY',
        columns='RISK_LEVEL',
        aggfunc='mean'
    )

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_table, annot=True, cmap='YlGnBu', fmt='.2f')
    plt.title("Fraud Rate by Injury Severity and Risk Level")
    plt.savefig(os.path.join(OUTPUT_DIR, 'fraud_injury_risk.png'))
    print("Fraud cross-feature analysis saved.")
    plt.show()


def feature_importance_analysis(df):
    """Perform feature importance analysis using RandomForest."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder

    print(" Analyzing feature importance...")
    # Encode categorical variables
    categorical_features = df.select_dtypes(include=['object']).columns
    df_encoded = df.copy()
    label_encoders = {}
    for feature in categorical_features:
        le = LabelEncoder()
        df_encoded[feature] = le.fit_transform(df_encoded[feature].astype(str))
        label_encoders[feature] = le

    # RandomForest for feature importance
    rf = RandomForestClassifier(random_state=42)
    X = df_encoded.drop(columns=['CLM_FRAUD_IND'])
    y = df_encoded['CLM_FRAUD_IND']
    rf.fit(X, y)

    feature_importance = pd.Series(rf.feature_importances_, index=X.columns)
    feature_importance.sort_values(ascending=False, inplace=True)

    plt.figure(figsize=(12, 6))
    feature_importance.plot(kind='bar', color='teal')
    plt.title("Feature Importance")
    plt.savefig(os.path.join(OUTPUT_DIR, 'feature_importance.png'))
    print(" Feature importance analysis saved.")
    plt.show()


def fraud_probability_by_feature(df):
    """Calculate and visualize fraud probability by feature values."""
    print(" Analyzing fraud probability by key features...")
    key_features = ['RISK_LEVEL', 'INJURY_SEVERITY']

    for feature in key_features:
        fraud_prob = df.groupby(feature)['CLM_FRAUD_IND'].mean()

        plt.figure(figsize=(8, 6))
        fraud_prob.plot(kind='bar', color='orange')
        plt.title(f"Fraud Probability by {feature}")
        plt.xlabel(feature)
        plt.ylabel("Fraud Probability")
        plt.savefig(os.path.join(OUTPUT_DIR, f'fraud_probability_{feature}.png'))
        print(f" Fraud probability plot for {feature} saved.")
        plt.show()


if __name__ == "__main__":
    # Load data
    df = load_data(DATA_PATH)

    if df is not None:
        # Add a derived feature: Days Between Occurrence and Report
        df['DAYS_BETWEEN_OCCUR_AND_REPORT'] = (
                pd.to_datetime(df['CLM_RPT_DT']) - pd.to_datetime(df['CLM_OCCR_DT'])
        ).dt.days

        # Run analyses
        correlation_analysis(df)
        outlier_detection(df)
        temporal_analysis(df)
        state_level_fraud_analysis(df)
        cross_feature_analysis(df)
        feature_importance_analysis(df)
        fraud_probability_by_feature(df)
