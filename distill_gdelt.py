import pandas as pd
master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
test_df = pd.read_csv(master_path, sep='\t', header=None, nrows=1000)
# Print the unique years in the first 1000 rows
print("Years found in sample:", (test_df[0] // 10000).unique())
