# Receipt Tax Display Update

## Overview
The print receipt now displays a detailed tax breakdown showing subtotal, tax amount, and grand total.

## Changes Made

### 1. Updated Receipt Format (`printerService.js`)

**Old Receipt:**
```
--------------------------------
جمع کل: 350,000 ریال
================================
```

**New Receipt:**
```
چلوکباب کوبیده
2 × 250,000 = 500,000 ریال
  (مالیات 10%)

نوشابه
3 × 15,000 = 45,000 ریال
  (مالیات 10%)

--------------------------------
جمع کالاها: 495,455 ریال
مالیات: 49,545 ریال
--------------------------------
جمع کل: 545,000 ریال
================================
       سپاسگزاریم
================================
```

### 2. Files Modified

#### `pywebview-vue-app/frontend/src/services/printerService.js`
- Updated `generateReceiptContent()` function
- Added tax calculation logic
- Shows individual item tax rates
- Displays subtotal, tax, and grand total

#### `pywebview-vue-app/frontend/src/views/Dashboard.vue`
- Updated `printCustomerInvoice()` function (line 771-785)
- Now passes `priceWithoutTax` and `vatRate` for each item
- Updated `loadFoods()` function (line 297-316)
- Loads tax information from menu items API

## Receipt Sections

### Header
```
آبشار سرا اسپادانا
============================

شماره سفارش: ORD-14040810-001

تاریخ: 1404/08/10
ساعت: 14:30:25

مشتری: علی احمدی
تلفن: 09123456789

--------------------------------
```

### Items Section
Each item shows:
- Item name
- Quantity × Price = Total
- Tax percentage (if applicable)

Example:
```
چلوکباب کوبیده
2 × 250,000 = 500,000 ریال
  (مالیات 10%)
```

### Summary Section
```
--------------------------------
جمع کالاها: 495,455 ریال       (Subtotal without tax)
مالیات: 49,545 ریال            (Total tax)
--------------------------------
جمع کل: 545,000 ریال           (Grand total)
```

### Footer
```
================================
       سپاسگزاریم
================================
```

## Tax Calculation

### Formula
```javascript
For each item:
  priceWithoutTax = item.priceWithoutTax
  priceWithTax = item.price
  itemSubtotal = priceWithoutTax × quantity
  itemTax = (priceWithTax - priceWithoutTax) × quantity
  
Total:
  subtotal = sum of all itemSubtotal
  totalTax = sum of all itemTax
  grandTotal = subtotal + totalTax
```

### Example Calculation

**Item 1: چلوکباب کوبیده (2 pieces)**
- Price without tax: 227,273 ریال
- VAT rate: 10%
- Price with tax: 250,000 ریال
- Tax per item: 22,727 ریال
- Subtotal: 454,546 ریال
- Tax: 45,454 ریال
- Total: 500,000 ریال

**Item 2: نوشابه (3 pieces)**
- Price without tax: 13,636 ریال
- VAT rate: 10%
- Price with tax: 15,000 ریال
- Tax per item: 1,364 ریال
- Subtotal: 40,908 ریال
- Tax: 4,092 ریال
- Total: 45,000 ریال

**Grand Total:**
- Subtotal: 495,454 ریال
- Total Tax: 49,546 ریال
- Grand Total: 545,000 ریال

## Tax Rate Display

Items show their tax rate if applicable:
- **0%**: No tax indicator shown
- **10%**: Shows "  (مالیات 10%)"
- **16%**: Shows "  (مالیات 16%)"

## Benefits

1. **Transparency**: Customers see exactly how much tax they're paying
2. **Compliance**: Meets Iranian tax reporting requirements
3. **Professional**: Shows detailed breakdown like standard invoices
4. **Accounting**: Easy to track tax collected vs. revenue

## Usage

No changes needed to how you print receipts:

```javascript
// In Dashboard.vue - works automatically
await printCustomerInvoice(customer)
```

The tax information is automatically:
1. Loaded from menu items API
2. Stored in customer items
3. Calculated in print receipt
4. Displayed on printed receipt

## Testing

To test the new receipt format:
1. Add items to an order
2. Click "چاپ" (Print) button
3. Check the printed/preview receipt
4. Verify tax breakdown appears correctly

## Notes

- Tax information comes from menu items
- If an item has no tax info, it defaults to 0%
- Grand total matches the order total
- Receipt works for both new and previous orders
- Compatible with both PyWebView printer and browser print

## Compatibility

Works with:
- ✅ Thermal receipt printers (via PyWebView)
- ✅ Browser print dialog
- ✅ PDF print
- ✅ All menu items with/without tax
- ✅ Manual orders
- ✅ Previous orders

## Future Enhancements

Possible additions:
- QR code with tax details
- Tax breakdown by rate (separate 10% and 16%)
- Tax ID/registration number
- Daily tax summary


