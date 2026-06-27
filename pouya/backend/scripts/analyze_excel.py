#!/usr/bin/env python
"""
Script to analyze the Excel file and understand why there are 481 rows instead of 200
"""
import pandas as pd
import os
import sys

def analyze_excel():
    """Analyze the Excel file in detail"""
    excel_file = 'foods.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file '{excel_file}' not found!")
        return
    
    print(f"📊 Analyzing Excel file: {excel_file}")
    print("=" * 60)
    
    # Read Excel file
    df = pd.read_excel(excel_file, engine='openpyxl')
    
    print(f"📈 Total rows in Excel: {len(df)}")
    print(f"📋 Total columns: {len(df.columns)}")
    print(f"📝 Column names: {list(df.columns)}")
    print()
    
    # Check for empty rows
    empty_rows = df.isnull().all(axis=1).sum()
    print(f"🔍 Empty rows: {empty_rows}")
    
    # Check for rows with missing essential data
    essential_columns = ['شناسه', 'نام', 'نام گروه']
    missing_essential = df[essential_columns].isnull().any(axis=1).sum()
    print(f"⚠️  Rows missing essential data: {missing_essential}")
    
    # Check for duplicate product codes
    if 'شناسه' in df.columns:
        duplicate_codes = df['شناسه'].duplicated().sum()
        print(f"🔄 Duplicate product codes: {duplicate_codes}")
        
        if duplicate_codes > 0:
            print("   Duplicate codes:")
            duplicates = df[df['شناسه'].duplicated(keep=False)]['شناسه'].unique()
            for code in duplicates[:10]:  # Show first 10
                print(f"     - {code}")
    
    # Check for duplicate names
    if 'نام' in df.columns:
        duplicate_names = df['نام'].duplicated().sum()
        print(f"🔄 Duplicate food names: {duplicate_names}")
        
        if duplicate_names > 0:
            print("   Duplicate names:")
            duplicates = df[df['نام'].duplicated(keep=False)]['نام'].unique()
            for name in duplicates[:10]:  # Show first 10
                print(f"     - {name}")
    
    # Analyze categories
    if 'نام گروه' in df.columns:
        categories = df['نام گروه'].value_counts()
        print(f"\n📂 Categories ({len(categories)} total):")
        for cat, count in categories.items():
            print(f"   {cat}: {count} items")
    
    # Check price data
    if 'جمع مبلغ ورود' in df.columns:
        price_col = 'جمع مبلغ ورود'
        price_stats = df[price_col].describe()
        print(f"\n💰 Price statistics:")
        print(f"   Min: {price_stats['min']}")
        print(f"   Max: {price_stats['max']}")
        print(f"   Mean: {price_stats['mean']:.2f}")
        print(f"   Items with price > 0: {(df[price_col] > 0).sum()}")
        print(f"   Items with price = 0: {(df[price_col] == 0).sum()}")
        print(f"   Items with missing price: {df[price_col].isnull().sum()}")
    
    # Show sample data
    print(f"\n📋 Sample data (first 10 rows):")
    print("-" * 80)
    sample_cols = ['شناسه', 'نام', 'نام گروه', 'جمع مبلغ ورود']
    available_cols = [col for col in sample_cols if col in df.columns]
    print(df[available_cols].head(10).to_string(index=False))
    
    # Check for potential data quality issues
    print(f"\n🔍 Data Quality Analysis:")
    
    # Check for very long names
    if 'نام' in df.columns:
        long_names = df[df['نام'].str.len() > 50]
        print(f"   Long names (>50 chars): {len(long_names)}")
    
    # Check for very high prices
    if 'جمع مبلغ ورود' in df.columns:
        high_prices = df[df['جمع مبلغ ورود'] > 10000000]  # > 10M
        print(f"   Very high prices (>10M): {len(high_prices)}")
    
    # Check for empty names
    if 'نام' in df.columns:
        empty_names = df[df['نام'].isnull() | (df['نام'].str.strip() == '')]
        print(f"   Empty or whitespace names: {len(empty_names)}")
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    analyze_excel()
