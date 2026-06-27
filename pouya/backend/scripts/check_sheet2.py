import pandas as pd

# Read Sheet2 to see its structure
df = pd.read_excel('foods.xlsx', sheet_name='Sheet2', engine='openpyxl')

print(f'Sheet2 has {len(df)} rows')
print(f'Columns: {list(df.columns)}')
print('\nFirst 5 rows:')
print(df.head().to_string())
