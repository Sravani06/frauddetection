#!/bin/bash

# Set the data directory
DATA_DIR="data"

# List of CSV files and their corresponding scripts
scripts=(
  "POLICY_DETAILS.csv:generate_policy_details.py"
  "CLAIM_DETAILS.csv:generate_claim_details.py"
  "CUSTOMER_DETAILS.csv:generate_customer_details.py"
  "CLAIM_STATUS.csv:generate_claim_status.py"
  "CLAIM_PARTICIPANT.csv:generate_claim_participant.py"
  "CLAIM_ADDITIONAL_DETAILS.csv:generate_claim_additional_details.py"
  "CLAIM_INJURY_DETAILS.csv:generate_claim_injury_details.py"
  "PAYMENT_DETAILS.csv:generate_payment_details.py"
)

# Ensure the data directory exists
mkdir -p "$DATA_DIR"

echo "=== Starting Data Generation ==="

# Iterate over the scripts and regenerate CSVs
for entry in "${scripts[@]}"; do
  IFS=":" read -r csv_file script <<< "$entry"

  # Check if the file exists and delete it
  if [ -f "$DATA_DIR/$csv_file" ]; then
    echo "Deleting existing file: $DATA_DIR/$csv_file"
    rm "$DATA_DIR/$csv_file"
  fi

  # Debug: Print current working directory
  echo "Current Directory: $(pwd)"

  # Run the script
  echo "Generating $csv_file using $script"
  python "scripts/$script"
  if [ $? -ne 0 ]; then
    echo "Error: $script failed to run. Exiting."
    exit 1
  fi

  # Check if the file was created successfully
  if [ -f "$DATA_DIR/$csv_file" ]; then
    echo "$csv_file generated successfully."
  else
    echo "Error: Failed to generate $csv_file. Exiting."
    exit 1
  fi
done

echo "=== Data Generation Complete ==="
