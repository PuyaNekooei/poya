# Daily Sales Report Guide

## Overview
Export a detailed daily sales report showing how many of each food item was sold on each day, along with the revenue generated.

## Report Location
**Django Admin → Orders → Orders**

## Report Columns (Persian Headers)

The export includes:
- **تاریخ شمسی** - Persian/Jalali Date (e.g., 1404/08/09)
- **نام غذا** - Food Item Name
- **کد محصول** - Product Code
- **دسته‌بندی** - Category
- **قیمت بدون مالیات** - Price Without Tax (unit price)
- **درصد مالیات** - Tax Percentage (0%, 10%, or 16%)
- **قیمت با مالیات** - Price With Tax (unit price)
- **تعداد فروش** - Quantity Sold
- **مجموع درآمد** - Total Revenue

## How to Use

### Step 1: Filter Orders by Date (Optional)
1. Go to **Django Admin → Orders → Orders**
2. Use the **date filter** on the right sidebar:
   - Click on "created at" filter
   - Select "Today", "Past 7 days", "This month", etc.
   - Or use custom date range

### Step 2: Select Orders
- **Select All**: Check the box at the top to select all filtered orders
- **Select Specific**: Check boxes next to specific orders
- **Filter First**: Apply filters, then select all to get specific time periods

### Step 3: Export Report
1. Click **Actions** dropdown (above the order list)
2. Select: **"گزارش فروش روزانه (Excel)"**
3. Click **"Go"**
4. File downloads automatically as: `daily_sales_report_YYYYMMDD.xlsx`

## Example Report

| تاریخ شمسی | نام غذا | کد محصول | دسته‌بندی | قیمت بدون مالیات | درصد مالیات | قیمت با مالیات | تعداد فروش | مجموع درآمد |
|------------|--------------|----------|-----------|------------------|------------|----------------|-----------|------------|
| 1404/08/10 | چلوکباب کوبیده | KB001 | غذای اصلی | 227,273 | 10% | 250,000 | 15 | 3,750,000 |
| 1404/08/10 | جوجه کباب | JK002 | غذای اصلی | 200,000 | 10% | 220,000 | 12 | 2,640,000 |
| 1404/08/10 | نوشابه | NS003 | نوشیدنی | 13,636 | 10% | 15,000 | 23 | 345,000 |
| 1404/08/09 | چلوکباب کوبیده | KB001 | غذای اصلی | 227,273 | 10% | 250,000 | 18 | 4,500,000 |
| 1404/08/09 | نوشابه | NS003 | نوشیدنی | 13,636 | 10% | 15,000 | 30 | 450,000 |

## Report Features

### 1. Styled Excel Output
- **Blue header row** with white text
- **Auto-sized columns** for readability
- **Professional formatting** ready to print

### 2. Sorted by Date
- Most recent dates appear first (descending order)
- Within each date, items sorted alphabetically by name

### 3. Aggregated Data
- If the same item was sold multiple times in a day, quantities are summed
- Revenue is totaled per item per day

### 4. Handles Unknown Products
- If an order item has no linked menu item
- Shows product name from `product_info`
- Marked as "محصول ناشناخته" if no name available

## Use Cases

### 1. Daily Sales Summary
**Goal**: See what sold today
```
1. Filter: Today
2. Select All
3. Export Daily Sales Report
```

### 2. Weekly Performance
**Goal**: Analyze this week's sales
```
1. Filter: Past 7 days
2. Select All
3. Export → Open in Excel
4. Use Pivot Table to analyze by day/item
```

### 3. Monthly Analysis
**Goal**: Compare sales across the month
```
1. Filter: This month
2. Select All
3. Export → Open in Excel
4. Create charts showing trends
```

### 4. Best Sellers by Day
**Goal**: Find which items sell best each day
```
1. Export weekly/monthly data
2. In Excel: Sort by تعداد فروش (descending)
3. Filter by specific dates
```

### 5. Revenue Analysis
**Goal**: See which items generate most revenue
```
1. Export sales data
2. Sort by مجموع درآمد (descending)
3. Identify top revenue generators
```

## Excel Tips

### Create Pivot Table
1. Open exported file in Excel
2. Select all data (Ctrl+A)
3. Insert → Pivot Table
4. Rows: تاریخ
5. Columns: نام غذا
6. Values: Sum of تعداد فروش

### Create Chart
1. Select data range
2. Insert → Chart
3. Recommended: Column chart for daily comparison
4. Line chart for trends over time

### Filter by Date Range
1. Click header row
2. Data → AutoFilter
3. Click dropdown on تاریخ column
4. Select specific dates

### Calculate Totals
```excel
=SUM(E2:E100)  // Total quantity sold
=SUM(F2:F100)  // Total revenue
```

## Report Scope

### What's Included
✅ All order items from selected orders
✅ Items with linked menu items
✅ Items without menu items (from product_info)
✅ All order statuses (pending, completed, cancelled, etc.)

### Important Notes
- **All statuses included**: Unlike some reports, this includes ALL orders you select
- **Based on order date**: Groups by the order's `created_at` date
- **Real-time data**: Report reflects current database state
- **No time filtering**: Groups by date only, not time of day

## Date Format

Dates appear in **Persian/Jalali Calendar** format: `YYYY/MM/DD`

Examples:
- `1404/08/10` = 10 Aban 1404 (November 1, 2025 Gregorian)
- `1404/08/09` = 9 Aban 1404 (October 31, 2025 Gregorian)

### Persian Calendar Months:
1. فروردین (Farvardin)
2. اردیبهشت (Ordibehesht)
3. خرداد (Khordad)
4. تیر (Tir)
5. مرداد (Mordad)
6. شهریور (Shahrivar)
7. مهر (Mehr)
8. آبان (Aban)
9. آذر (Azar)
10. دی (Dey)
11. بهمن (Bahman)
12. اسفند (Esfand)

## Troubleshooting

### Empty Report
**Problem**: No data in exported file
**Solutions**:
- Make sure you selected orders before running action
- Check if selected orders have order items
- Verify orders aren't empty

### Missing Menu Items
**Problem**: Some items show as "محصول ناشناخته"
**Solutions**:
- These are items not linked to menu items
- Check OrderItem.product_info for details
- Consider linking products to menu items

### Revenue Doesn't Match
**Problem**: Revenue seems wrong
**Explanation**:
- Revenue is from OrderItem.total_price
- Already includes quantity × unit_price
- Check individual order items if discrepancies exist

### Very Large File
**Problem**: Excel file is huge
**Solutions**:
- Filter by shorter date range before export
- Select fewer orders
- Consider splitting into weekly exports

## Comparison with Other Reports

| Report Type | Location | Shows |
|------------|----------|-------|
| **Daily Sales Report** | Orders Admin | Sales per day per item |
| Standard Order Export | Orders Admin | Full order details |
| Menu Item Export | Menu Admin | Menu item master data |

## Next Steps

After exporting:
1. **Analyze trends**: Which items sell consistently?
2. **Identify patterns**: What sells more on certain days?
3. **Inventory planning**: Adjust stock based on sales
4. **Pricing decisions**: Evaluate pricing strategy
5. **Menu optimization**: Consider removing slow sellers

## Advanced Usage

### Combine with Filters
```
1. Filter by order_type = 'manual'
2. Filter by created_at = 'This month'
3. Export → Compare orders across the month
```

### Compare Time Periods
```
1. Export November orders → Save as "Nov.xlsx"
2. Export October orders → Save as "Oct.xlsx"
3. Use Excel VLOOKUP to compare
```

### Create Dashboard
```
1. Export monthly data
2. Create Pivot Table
3. Add Slicers for Date/Category
4. Build charts
5. Save as dashboard template
```

## File Naming

Export files are named using **Persian/Jalali date**:
```
daily_sales_report_YYYYMMDD.xlsx
```
Where YYYYMMDD is the Persian calendar export date.

Examples:
- `daily_sales_report_14040810.xlsx` - Exported on 10 Aban 1404
- `daily_sales_report_14040809.xlsx` - Exported on 9 Aban 1404

## Support

If you need different report formats:
- Different date grouping (weekly, monthly)
- Different aggregations (by category, by day of week)
- Additional filters (by status, by order type)

You can modify the code in `orders/admin.py` → `export_daily_sales_report` method.

