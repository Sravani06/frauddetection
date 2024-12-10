#!/bin/bash

# Activate the Python virtual environment
echo " Activating Python virtual environment..."
source .venv/bin/activate

# Step 1: Generate synthetic data
echo " Step 1: Generating synthetic data..."
python scripts/generate_fraud_detection_dataset.py
if [ $? -ne 0 ]; then
    echo " Error generating synthetic data. Exiting..."
    exit 1
fi

# Step 2: Enhance the unified dataset
echo " Step 2: Enhancing unified dataset with derived features..."
python scripts/generate_enhanced_unified_dataset.py
if [ $? -ne 0 ]; then
    echo " Error enhancing the unified dataset. Exiting..."
    exit 1
fi

# Step 3: Apply fraud detection rules
echo "Step 3: Applying fraud detection rules..."
python scripts/fraud_rules.py
if [ $? -ne 0 ]; then
    echo " Error applying fraud detection rules. Exiting..."
    exit 1
fi

# Step 4: Preprocess the data
echo " Step 4: Preprocessing data for machine learning..."
python scripts/preprocess_data.py
if [ $? -ne 0 ]; then
    echo " Error preprocessing dataset. Exiting..."
    exit 1
fi

# Step 5: Perform feature selection
echo " Step 5: Selecting important features..."
python scripts/feature_selection.py
if [ $? -ne 0 ]; then
    echo " Error selecting features. Exiting..."
    exit 1
fi

# Step 6: Train and save the machine learning model
echo " Step 6: Training the machine learning model..."
python scripts/model_training.py
if [ $? -ne 0 ]; then
    echo " Error training the machine learning model. Exiting..."
    exit 1
fi

# Step 7: Deploy and run the Streamlit dashboard
echo "Step 7: Launching the Streamlit dashboard..."
streamlit run app/dashboard.py --server.port 8501 --server.headless true
if [ $? -ne 0 ]; then
    echo " Error launching the Streamlit
    exit 1
fi

echo " All steps completed successfully!"
