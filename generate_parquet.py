import pandas as pd

# Read the CSV file
df = pd.read_csv("data\\sample.csv")

# Save as Parquet format
df.to_parquet("data\\sample.parquet", index=False)

print("✅ Parquet file created successfully!")
