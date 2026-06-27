# VAT (Value Added Tax) Automatic Calculation Feature

## Overview
The MenuItem model now automatically calculates `price_with_tax` based on `price_without_tax` and the selected VAT rate.

## Changes Made

### 1. Model Updates (`menu/models.py`)

#### New Field: `vat_rate`
- **Type**: IntegerField with choices
- **Choices**:
  - `0%` - بدون مالیات (No tax)
  - `10%` - مالیات 10%
  - `16%` - مالیات 16%
- **Default**: 10%
- **Purpose**: Stores the VAT percentage for each menu item

#### Updated Field: `price_with_tax`
- **Changed to**: `editable=False` (read-only in admin)
- **Purpose**: Automatically calculated, users can't manually edit it

#### New Save Method
```python
def save(self, *args, **kwargs):
    # Automatically calculate price_with_tax based on vat_rate
    if self.price_without_tax:
        vat_multiplier = 1 + (self.vat_rate / 100)
        self.price_with_tax = self.price_without_tax * vat_multiplier
    super().save(*args, **kwargs)
```

### 2. Admin Updates (`menu/admin.py`)

- Added `vat_rate` to `list_display` - now visible in admin list view
- Added `vat_rate` to `list_filter` - can filter by VAT rate
- Added `vat_rate` to export fields - included in Excel exports
- Made `price_with_tax` read-only in admin forms

### 3. Database Migration

Created migration: `0007_menuitem_vat_rate_alter_menuitem_price_with_tax.py`
- Adds `vat_rate` field with default value of 10%
- Marks `price_with_tax` as non-editable

## How It Works

### Calculation Formula
```
price_with_tax = price_without_tax × (1 + vat_rate / 100)
```

### Examples

#### Example 1: 10% VAT (Default)
- Price without tax: 100,000 تومان
- VAT rate: 10%
- **Price with tax: 110,000 تومان** (automatically calculated)

#### Example 2: 16% VAT
- Price without tax: 100,000 تومان
- VAT rate: 16%
- **Price with tax: 116,000 تومان** (automatically calculated)

#### Example 3: 0% VAT (Tax-free items)
- Price without tax: 100,000 تومان
- VAT rate: 0%
- **Price with tax: 100,000 تومان** (automatically calculated)

## Usage in Django Admin

### Creating a New Menu Item

1. Go to Django Admin → Menu → Menu Items → Add
2. Fill in the details:
   - نام غذا (Name)
   - کد محصول (Product code)
   - دسته‌بندی (Category)
   - **قیمت بدون مالیات** (Price without tax) - Enter the base price
   - **نرخ مالیات** (VAT rate) - Select 0%, 10%, or 16%
3. Save
4. **قیمت با مالیات** (Price with tax) will be automatically calculated!

### Editing an Existing Menu Item

1. Open the menu item
2. Change `price_without_tax` or `vat_rate`
3. Save
4. `price_with_tax` recalculates automatically

### Filtering by VAT Rate

In the admin list view:
- Use the right sidebar filter
- Select VAT rate (0%, 10%, or 16%)
- View only items with that tax rate

## Excel Export

When exporting menu items to Excel, the export now includes:
- قیمت بدون مالیات (Price without tax)
- نرخ مالیات بر ارزش افزوده (VAT rate)
- قیمت با مالیات (Price with tax)

This makes it easy to see tax breakdown in reports.

## API Response

The serializer will include all three values:
```json
{
  "id": 1,
  "name": "چلوکباب کوبیده",
  "price_without_tax": "100000.00",
  "vat_rate": 10,
  "price_with_tax": "110000.00"
}
```

## Migration Instructions

To apply this feature to your database:

```bash
# Navigate to backend directory
cd backend

# Apply the migration
python manage.py migrate menu

# Or for all apps
python manage.py migrate
```

## Important Notes

1. **Existing Records**: All existing menu items will default to 10% VAT
2. **Price Updates**: Whenever you save a menu item, the price_with_tax recalculates
3. **Read-Only Field**: Users cannot manually edit price_with_tax in the admin
4. **Decimal Precision**: Prices use 2 decimal places for accuracy
5. **Order Integration**: The `price_with_tax` is used when creating orders

## Testing

A test script is provided: `test_vat_calculation.py`

Run it to verify calculations:
```bash
python test_vat_calculation.py
```

## Support

If you need to add more VAT rates in the future, edit `VAT_RATE_CHOICES` in `menu/models.py`:

```python
VAT_RATE_CHOICES = [
    (0, _('بدون مالیات (0%)')),
    (10, _('مالیات 10%')),
    (16, _('مالیات 16%')),
    # Add new rates here:
    # (9, _('مالیات 9%')),
]
```

Then create a new migration:
```bash
python manage.py makemigrations menu
python manage.py migrate menu
```



