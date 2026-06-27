# -*- coding: utf-8 -*-
"""
Django management command to import foods from Excel file
"""
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from menu.models import Category, MenuItem
import os
import sys

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')


class Command(BaseCommand):
    help = 'Import foods from Excel file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='foods.xlsx',
            help='Path to Excel file (default: foods.xlsx)'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default='Sheet2',
            help='Sheet name to read from (default: Sheet2)'
        )
        parser.add_argument(
            '--auto-detect-columns',
            action='store_true',
            help='Auto-detect column names instead of using default mapping'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing menu items before importing'
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Import only active items (with price > 0)'
        )
        parser.add_argument(
            '--handle-duplicates',
            choices=['skip', 'update', 'create'],
            default='update',
            help='How to handle duplicate names: skip, update, or create separate items'
        )

    def handle(self, *args, **options):
        excel_file = options['file']
        sheet_name = options['sheet']
        auto_detect = options['auto_detect_columns']
        dry_run = options['dry_run']
        clear_existing = options['clear_existing']
        active_only = options['active_only']
        handle_duplicates = options['handle_duplicates']

        # Check if file exists
        if not os.path.exists(excel_file):
            raise CommandError(f'Excel file "{excel_file}" not found')

        try:
            # Read Excel file
            self.stdout.write(f'Reading Excel file: {excel_file} from sheet: {sheet_name}')
            df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
            
            self.stdout.write(f'Found {len(df)} rows in Excel file')
            
            if auto_detect:
                # Show available columns for user to see
                self.stdout.write(f'Available columns: {list(df.columns)}')
                self.stdout.write('Please check the column names and update the mapping if needed.')
                return
            
            # Map column names based on sheet
            if sheet_name == 'Sheet2':
                column_mapping = {
                    'شناسه': 'product_code',
                    'نام': 'name', 
                    'نام گروه': 'category_name',
                    'قیمت با ارزش افزوده': 'price_with_tax',
                    'قیمت بدون ارزش افزوده': 'price_without_tax',
                    'نام واحد': 'unit_name'
                }
            else:
                # Default mapping for Sheet1
                column_mapping = {
                    'شناسه': 'product_code',
                    'نام': 'name', 
                    'نام گروه': 'category_name',
                    'جمع مبلغ ورود': 'price_with_tax'
                }
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Remove rows with missing essential data
            df = df.dropna(subset=['name', 'category_name'])
            
            # Normalize price columns without heuristic scaling
            try:
                # Ensure both price columns exist
                if 'price_with_tax' not in df.columns:
                    df['price_with_tax'] = None
                if 'price_without_tax' not in df.columns:
                    df['price_without_tax'] = None

                # If not Sheet2, we cannot trust totals as unit prices; drop them
                if sheet_name != 'Sheet2':
                    df['price_with_tax'] = None
                    df['price_without_tax'] = None

                # Coerce both to numeric
                df['price_with_tax'] = pd.to_numeric(df['price_with_tax'], errors='coerce')
                df['price_without_tax'] = pd.to_numeric(df['price_without_tax'], errors='coerce')

                # Fill missing without_tax with with_tax; remaining NaN -> 0 for required field
                df['price_without_tax'] = df['price_without_tax'].fillna(df['price_with_tax'])
                df['price_with_tax'] = df['price_with_tax'].fillna(0)
                df['price_without_tax'] = df['price_without_tax'].fillna(0)

                # Clip to DecimalField limits (max_digits=10, decimal_places=2)
                df['price_with_tax'] = df['price_with_tax'].clip(lower=0, upper=99999999.99)
                df['price_without_tax'] = df['price_without_tax'].clip(lower=0, upper=99999999.99)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing price data: {str(e)}'))
                raise
            
            # Convert product_code to string
            df['product_code'] = df['product_code'].astype(str)
            
            # Filter for active items only if requested
            if active_only:
                original_count = len(df)
                df = df[(df['price_with_tax'] > 0) | (df['price_without_tax'] > 0)]
                filtered_count = len(df)
                self.stdout.write(f'Filtered to active items only: {original_count} -> {filtered_count} items')
            
            # Handle duplicates based on strategy
            if handle_duplicates == 'skip':
                original_count = len(df)
                df = df.drop_duplicates(subset=['name'], keep='first')
                filtered_count = len(df)
                self.stdout.write(f'Removed duplicate names: {original_count} -> {filtered_count} items')
            elif handle_duplicates == 'create':
                # Add suffix to duplicate names to make them unique
                df = df.reset_index(drop=True)
                for i in range(len(df)):
                    name = df.loc[i, 'name']
                    if df[df['name'] == name].index.tolist().index(i) > 0:
                        df.loc[i, 'name'] = f"{name} ({df[df['name'] == name].index.tolist().index(i) + 1})"
                self.stdout.write(f'Added suffixes to duplicate names to make them unique')
            
            if dry_run:
                self.stdout.write('\n=== DRY RUN - No data will be imported ===')
                self.show_import_summary(df)
                return
            
            # Clear existing data if requested
            if clear_existing:
                self.stdout.write('Clearing existing menu items...')
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM menu_menuitem")
                        cursor.execute("DELETE FROM menu_category")
                    self.stdout.write('Existing data cleared successfully')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Warning: Could not clear existing data: {str(e)}'))
                    self.stdout.write('Continuing with import...')
            
            # Import data
            self.import_data(df)
            
        except Exception as e:
            import traceback
            self.stdout.write(self.style.ERROR(f'Error processing Excel file: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'Traceback: {traceback.format_exc()}'))
            raise CommandError(f'Error processing Excel file: {str(e)}')

    def show_import_summary(self, df):
        """Show summary of what would be imported"""
        categories = df['category_name'].unique()
        active_items = len(df[(df['price_with_tax'] > 0) | (df['price_without_tax'] > 0)])
        inactive_items = len(df) - active_items
        
        # Check for duplicates
        duplicate_names = df['name'].duplicated().sum()
        duplicate_codes = df['product_code'].duplicated().sum()
        empty_rows = df.isnull().all(axis=1).sum()
        
        self.stdout.write(f'\n=== DATA ANALYSIS ===')
        self.stdout.write(f'Total rows in Excel: {len(df)}')
        self.stdout.write(f'Empty rows: {empty_rows}')
        self.stdout.write(f'Duplicate food names: {duplicate_names}')
        self.stdout.write(f'Duplicate product codes: {duplicate_codes}')
        
        if duplicate_names > 0:
            self.stdout.write(f'\nDuplicate names found:')
            duplicates = df[df['name'].duplicated(keep=False)]['name'].unique()
            for name in duplicates[:10]:  # Show first 10
                count = len(df[df['name'] == name])
                self.stdout.write(f'  - "{name}" appears {count} times')
        
        if duplicate_codes > 0:
            self.stdout.write(f'\nDuplicate codes found:')
            duplicates = df[df['product_code'].duplicated(keep=False)]['product_code'].unique()
            for code in duplicates[:10]:  # Show first 10
                count = len(df[df['product_code'] == code])
                self.stdout.write(f'  - Code "{code}" appears {count} times')
        
        self.stdout.write(f'\n=== IMPORT SUMMARY ===')
        self.stdout.write(f'Categories to be created: {len(categories)}')
        for cat in categories:
            self.stdout.write(f'  - {cat}')
        
        self.stdout.write(f'\nMenu items to be imported: {len(df)}')
        self.stdout.write(f'  - Active items (with price): {active_items}')
        self.stdout.write(f'  - Inactive items (no price): {inactive_items}')
        
        # Show sample data
        self.stdout.write('\nSample data:')
        sample = df.head(5)
        for _, row in sample.iterrows():
            status = "ACTIVE" if (row['price_with_tax'] > 0) or (row.get('price_without_tax', 0) > 0) else "INACTIVE"
            self.stdout.write(f'  {row["name"]} - {row["category_name"]} - with_tax={row.get("price_with_tax", 0)} without_tax={row.get("price_without_tax", 0)} - {status}')

    @transaction.atomic
    def import_data(self, df):
        """Import data into database"""
        categories_created = 0
        items_created = 0
        items_updated = 0
        
        # Create categories
        category_map = {}
        for category_name in df['category_name'].unique():
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'دسته‌بندی {category_name}'}
            )
            category_map[category_name] = category
            if created:
                categories_created += 1
        
        self.stdout.write(f'Created {categories_created} new categories')
        
        # Import menu items
        for _, row in df.iterrows():
            try:
                # Convert price to proper decimal format
                from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
                import math
                with_tax_val = row.get('price_with_tax', 0)
                without_tax_val = row.get('price_without_tax', None)

                def to_decimal(value, default='0.00'):
                    try:
                        if pd.isna(value) or (isinstance(value, (int, float)) and math.isinf(value)):
                            value = default
                        return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    except (InvalidOperation, ValueError, TypeError):
                        return Decimal(default)

                price_with_tax = to_decimal(with_tax_val, '0.00')
                # If without_tax missing, fall back to with_tax to satisfy NOT NULL
                price_without_tax = to_decimal(without_tax_val if without_tax_val is not None else with_tax_val, '0.00')

                # Determine if item should be active based on either price
                is_active = (price_with_tax > 0) or (price_without_tax > 0)
                is_available = is_active
                
                # Get or create menu item
                menu_item, created = MenuItem.objects.get_or_create(
                    product_code=row['product_code'],
                    defaults={
                        'name': row['name'],
                        'category': category_map[row['category_name']],
                        'price_with_tax': price_with_tax,
                        'price_without_tax': price_without_tax,
                        'is_active': is_active,
                        'is_available': is_available,
                        'description': f'غذای {row["name"]}'
                    }
                )
                
                if created:
                    items_created += 1
                else:
                    # Update existing item
                    menu_item.name = row['name']
                    menu_item.category = category_map[row['category_name']]
                    menu_item.price_with_tax = price_with_tax
                    menu_item.price_without_tax = price_without_tax
                    menu_item.is_active = is_active
                    menu_item.is_available = is_available
                    menu_item.save()
                    items_updated += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importing item {row["name"]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nImport completed successfully!\n'
                f'Categories created: {categories_created}\n'
                f'Menu items created: {items_created}\n'
                f'Menu items updated: {items_updated}'
            )
        )
