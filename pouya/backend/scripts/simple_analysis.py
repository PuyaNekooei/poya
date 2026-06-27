import pandas as pd

# Read Excel file
df = pd.read_excel('foods.xlsx', engine='openpyxl')

print(f'Total rows in Excel: {len(df)}')
print(f'Columns: {list(df.columns)}')

# Check for duplicates
if 'نام' in df.columns:
    duplicate_names = df['نام'].duplicated().sum()
    print(f'Duplicate food names: {duplicate_names}')

if 'شناسه' in df.columns:
    duplicate_codes = df['شناسه'].duplicated().sum()
    print(f'Duplicate product codes: {duplicate_codes}')

# Check for empty rows
empty_rows = df.isnull().all(axis=1).sum()
print(f'Empty rows: {empty_rows}')

# Check categories
if 'نام گروه' in df.columns:
    categories = df['نام گروه'].value_counts()
    print(f'Number of categories: {len(categories)}')
    print('Categories:')
    for cat, count in categories.items():
        print(f'  {cat}: {count} items')

# Show first few rows
print('\nFirst 5 rows:')
print(df.head().to_string())

# Check for rows with missing essential data
essential_columns = ['شناسه', 'نام', 'نام گروه']
missing_essential = df[essential_columns].isnull().any(axis=1).sum()
print(f'\nRows missing essential data: {missing_essential}')

# Check price data
if 'جمع مبلغ ورود' in df.columns:
    price_col = 'جمع مبلغ ورود'
    items_with_price = (df[price_col] > 0).sum()
    items_without_price = (df[price_col] == 0).sum()
    print(f'Items with price > 0: {items_with_price}')
    print(f'Items with price = 0: {items_without_price}')
