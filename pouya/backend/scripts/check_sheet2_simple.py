import pandas as pd

# Read Sheet2 to see its structure
df = pd.read_excel('foods.xlsx', sheet_name='Sheet2', engine='openpyxl')

print(f'Sheet2 has {len(df)} rows')
print('Columns:')
for i, col in enumerate(df.columns):
    print(f'  {i}: {repr(col)}')

print('\nFirst 3 rows:')
for i in range(min(3, len(df))):
    print(f'Row {i}:')
    for col in df.columns:
        print(f'  {repr(col)}: {repr(df.iloc[i][col])}')
    print()
