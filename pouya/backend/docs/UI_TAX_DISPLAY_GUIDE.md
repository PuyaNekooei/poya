# UI Tax Display Guide

## Overview
The Dashboard UI now displays detailed tax information throughout the ordering process, showing price breakdowns and tax percentages.

## Changes Made

### 1. Food Items Display (Menu Grid)

**Location**: Left panel - Food list

**Before:**
```
┌─────────────────┐
│ چلوکباب کوبیده  │
│ 250,000 ریال    │
│ موجودی: 50      │
└─────────────────┘
```

**After:**
```
┌─────────────────┐
│ چلوکباب کوبیده  │
│ 250,000 ریال    │
│ [مالیات 10%]    │  ← NEW!
│ موجودی: 50      │
└─────────────────┘
```

**Features:**
- Shows tax badge for items with VAT > 0%
- Blue badge with percentage
- Only appears if item has tax

### 2. Order Items Display (Customer Tab)

**Location**: Customer tab - Order items list

**Before:**
```
چلوکباب کوبیده
250,000 ریال
[Quantity] [Remove]
```

**After:**
```
چلوکباب کوبیده
250,000 ریال (مالیات 10%)  ← NEW!
[Quantity] [Remove]
```

**Features:**
- Tax percentage shown next to price
- Small blue badge
- Only appears if item has tax

### 3. Order Summary (Tax Breakdown)

**Location**: Customer tab - Bottom of order

**Before:**
```
جمع کل: 500,000 ریال
[Accept Order] [Print]
```

**After:**
```
جمع کالاها:    454,546 ریال  ← NEW!
مالیات:         45,454 ریال  ← NEW!
────────────────────────────
جمع کل:        500,000 ریال
[Accept Order] [Print]
```

**Features:**
- Three-row breakdown:
  1. **جمع کالاها** - Subtotal (without tax)
  2. **مالیات** - Total tax amount (blue color)
  3. **جمع کل** - Grand total (green, bold)
- Clear visual separation

## Visual Design

### Color Scheme

```css
Tax Badge (Food Items):
- Background: #e3f2fd (Light Blue)
- Text: #1976d2 (Blue)
- Border Radius: 12px
- Font Size: 11px

Tax Badge (Order Items):
- Background: #e3f2fd (Light Blue)
- Text: #1976d2 (Blue)
- Border Radius: 8px
- Font Size: 11px

Summary Rows:
- Subtotal: #495057 (Dark Gray)
- Tax: #1976d2 (Blue, Bold)
- Total: #2e7d32 (Green, Bold)
```

### Layout Details

**Food Item Card:**
```
┌──────────────────────┐
│ Food Name (Bold)     │
│ Price (Green, Bold)  │
│ Tax Badge (Blue)     │ ← Only if tax > 0%
│ Stock (Gray, Small)  │
└──────────────────────┘
```

**Order Item:**
```
[Name]              [Controls]
[Price] [(Tax %)]   [Qty] [✕]
```

**Tax Breakdown:**
```
Subtotal:    xxx ریال
Tax:         xxx ریال  (Blue)
─────────────────────
Total:       xxx ریال  (Green, Bold)
```

## Calculation Logic

### JavaScript Functions

```javascript
// Calculate subtotal (price without tax)
calculateSubtotal(customer) {
  return customer.items.reduce((sum, item) => {
    const priceWithoutTax = parseFloat(item.priceWithoutTax || item.price)
    return sum + (priceWithoutTax * item.quantity)
  }, 0)
}

// Calculate total tax
calculateTax(customer) {
  return customer.items.reduce((sum, item) => {
    const priceWithoutTax = parseFloat(item.priceWithoutTax || item.price)
    const priceWithTax = parseFloat(item.price)
    const taxAmount = (priceWithTax - priceWithoutTax) * item.quantity
    return sum + taxAmount
  }, 0)
}
```

### Example Calculation

**Order with 2 items:**
1. چلوکباب کوبیده (2x)
   - Price without tax: 227,273 ریال
   - VAT: 10%
   - Price with tax: 250,000 ریال
   - Subtotal: 454,546 ریال
   - Tax: 45,454 ریال

2. نوشابه (3x)
   - Price without tax: 13,636 ریال
   - VAT: 10%
   - Price with tax: 15,000 ریال
   - Subtotal: 40,908 ریال
   - Tax: 4,092 ریال

**Summary:**
- جمع کالاها: 495,454 ریال
- مالیات: 49,546 ریال
- جمع کل: 545,000 ریال

## Data Flow

### 1. Backend → Frontend

**API Response** (`/api/menu/with_inventory/`):
```json
{
  "id": 1,
  "name": "چلوکباب کوبیده",
  "price": 250000,
  "price_without_tax": 227273,
  "price_with_tax": 250000,
  "vat_rate": 10,
  "stock": 50
}
```

### 2. Frontend Storage

**Food Object:**
```javascript
{
  id: 1,
  name: 'چلوکباب کوبیده',
  price: 250000,
  priceWithoutTax: 227273,
  vatRate: 10,
  stock: 50
}
```

### 3. Order Item

**When added to customer:**
```javascript
{
  name: 'چلوکباب کوبیده',
  price: 250000,
  priceWithoutTax: 227273,
  vatRate: 10,
  quantity: 2
}
```

## User Experience

### For Cashier

1. **Menu Browse**: Can see which items have tax
2. **Order Building**: Tax shown for each item
3. **Summary**: Clear breakdown before checkout
4. **Transparency**: Customer can see tax calculation

### Benefits

✅ **Clarity**: Tax amounts clearly visible
✅ **Transparency**: Customers know what they're paying
✅ **Compliance**: Meets tax display requirements
✅ **Professional**: Modern, clean design
✅ **Informative**: Shows percentage and amount

## Responsive Behavior

### Food Grid
- Tax badge scales with card size
- Maintains readability at all sizes
- Wraps properly in narrow views

### Order Summary
- Three-row layout always visible
- Proper alignment on all screen sizes
- Bold total stands out

## Edge Cases Handled

### No Tax Items (0%)
- Tax badge **not shown** on food card
- Tax badge **not shown** in order items
- Tax row still shown in summary (0 ریال)

### Mixed Tax Rates
- Each item shows its own tax percentage
- Total tax is sum of all individual taxes
- Works with 0%, 10%, and 16%

### Unknown Items
- Falls back to showing full price if tax info missing
- Displays tax as 0% if not available

## CSS Classes Reference

```css
/* Food Items */
.food-tax-info          /* Container for tax badge */
.tax-badge              /* Blue tax percentage badge */

/* Order Items */
.item-price-details     /* Price and tax container */
.item-tax-badge         /* Tax badge in order item */

/* Summary */
.tax-breakdown          /* Container for breakdown */
.summary-row            /* Each row in breakdown */
.tax-row                /* Tax-specific styling */
.total-row              /* Total row with border */
```

## Testing Checklist

- [ ] Food items show tax badge when VAT > 0%
- [ ] Food items hide tax badge when VAT = 0%
- [ ] Order items show tax percentage
- [ ] Summary shows three rows (subtotal, tax, total)
- [ ] Calculations are correct
- [ ] Colors match design (blue tax, green total)
- [ ] Text is in Persian/Farsi
- [ ] Layout works on different screen sizes
- [ ] Print receipt matches UI display

## Future Enhancements

Possible additions:
- Tax breakdown by rate (separate 10% and 16%)
- Visual indicator for high-tax items
- Tax-free item badge
- Export tax summary
- Monthly tax reports


