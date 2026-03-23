master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"

with open(master_path, 'r') as f:
    f.readline() # skip header
    line = f.readline()
    
parts = line.split('\t')
for i, val in enumerate(parts):
    print(f"Index {i}: {val}")
