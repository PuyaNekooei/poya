# Django Admin Excel Export Guide

## Overview
Excel export functionality has been added to all Django admin models using the `django-import-export` package.

## Features Added

### Menu App Models
- **Category**: Export categories with all details
- **MenuItem**: Export menu items with category names, prices, and availability status
- **DailyInventory**: Export daily inventory with menu item details

### Orders App Models
- **Order**: Export orders with customer info, amounts, and status
- **OrderItem**: Export order items with intelligent item name resolution

## How to Use

### Export Data to Excel

1. **Access Django Admin**: Navigate to your Django admin panel (usually `/admin/`)

2. **Select a Model**: Go to any of the models listed above (e.g., Menu Items, Orders, etc.)

3. **Export Options**: At the top right of the list view, you'll see export buttons:
   - Click on the dropdown menu to choose your format
   - Select **XLSX** for Excel format
   - Other formats available: CSV, JSON, YAML, TSV, ODS, HTML

4. **Filtered Exports**: You can also:
   - Apply filters to the list view
   - Search for specific items
   - Then export only the filtered results

### Import Data (Bonus Feature)

The package also supports importing data:
1. Click the "Import" button at the top of the list page
2. Upload your Excel file (XLSX format)
3. Review the changes before confirming
4. The system will show you what will be added/updated

## Export Formats

- **XLSX**: Microsoft Excel (recommended)
- **CSV**: Comma-separated values
- **JSON**: JavaScript Object Notation
- **YAML**: YAML format
- **TSV**: Tab-separated values
- **ODS**: OpenDocument Spreadsheet
- **HTML**: HTML table format

## Technical Details

### Installed Package
- **django-import-export** version 4.0.0
- Added to `requirements.txt`
- Added to `INSTALLED_APPS` in settings.py

### Resource Classes
Each model has a corresponding Resource class that defines:
- Which fields to export
- The order of columns in the export
- Custom field processing (e.g., resolving item names)

### Admin Classes
All admin classes now inherit from `ImportExportModelAdmin` instead of `ModelAdmin`, which provides:
- Export buttons in the admin interface
- Import functionality
- Format selection
- Progress tracking for large exports

## Customization

If you need to customize what fields are exported, edit the Resource classes in:
- `backend/menu/admin.py` - for menu-related exports
- `backend/orders/admin.py` - for order-related exports

Example Resource class structure:
```python
class MenuItemResource(resources.ModelResource):
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'product_code', 'category__name', 'price_with_tax')
        export_order = ('id', 'name', 'product_code', 'category__name', 'price_with_tax')
```

## Notes

- Exports respect Django admin permissions
- Large exports might take a moment to generate
- Date/time fields are exported in ISO format
- Related fields use `__` notation (e.g., `category__name`)
- JSON fields are exported as formatted text

## Support

For more information about django-import-export, visit:
https://django-import-export.readthedocs.io/



