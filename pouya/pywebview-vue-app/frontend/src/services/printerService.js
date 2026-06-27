// Printer service for PyWebView integration
const printerService = {
  
  // Print receipt using PyWebView API
  async printReceipt(receiptData) {
    try {
      console.log('Printing receipt:', receiptData)
      
      // Try PyWebView API first
      if (window.pywebview && window.pywebview.api) {
        const result = await window.pywebview.api.print_receipt(receiptData)
        
        if (result.success) {
          console.log('Receipt printed successfully via PyWebView')
          return result
        } else {
          console.error('PyWebView print failed:', result.error)
          throw new Error(result.error)
        }
      } else {
        // Fallback to browser print
        console.warn('PyWebView API not available, using browser print')
        return this.printViaBrowser(receiptData)
      }
      
    } catch (error) {
      console.error('Print receipt error:', error)
      throw error
    }
  },

  // Test printer connection
  async testPrinter() {
    try {
      console.log('Testing printer...')
      
      if (window.pywebview && window.pywebview.api) {
        const result = await window.pywebview.api.test_printer({
          content: 'تست چاپگر - Printer Test'
        })
        
        if (result.success) {
          console.log('Printer test successful')
          return result
        } else {
          console.error('Printer test failed:', result.error)
          throw new Error(result.error)
        }
      } else {
        // Fallback test
        console.warn('PyWebView API not available for printer test')
        return { success: true, message: 'Browser print available' }
      }
      
    } catch (error) {
      console.error('Printer test error:', error)
      throw error
    }
  },

  // Generate receipt content for printing
  generateReceiptContent(customer) {
    const now = new Date()
    const dateStr = now.toLocaleDateString('fa-IR')
    const timeStr = now.toLocaleTimeString('fa-IR')
    
    let content = `
پویا
============================

شماره سفارش: ${customer.orderNumber || 'N/A'}

تاریخ: ${dateStr}
ساعت: ${timeStr}

مشتری: ${customer.name}
تلفن: ${customer.phone}

--------------------------------
`

    // Add items and calculate totals
    let subtotal = 0  // Sum of (price_without_tax * quantity)
    let totalTax = 0  // Sum of tax amounts
    
    if (customer.items && customer.items.length > 0) {
      customer.items.forEach(item => {
        // Get prices from item data
        // NOTE: item.price is already the price WITH tax (from backend)
        const priceWithTax = parseFloat(item.price)  // This is price WITH tax
        const vatRate = parseFloat(item.vatRate || 0)
        const quantity = parseInt(item.quantity)
        
        // Get or calculate price without tax
        let priceWithoutTax = parseFloat(item.priceWithoutTax)
        if (!priceWithoutTax && vatRate > 0) {
          // Calculate: price_without_tax = price_with_tax / (1 + vat_rate/100)
          priceWithoutTax = priceWithTax / (1 + vatRate / 100)
        } else if (!priceWithoutTax) {
          // No tax info, assume price is without tax
          priceWithoutTax = priceWithTax
        }
        
        // Calculate for this item
        const itemSubtotal = priceWithoutTax * quantity  // قیمت بدون مالیات × تعداد
        const itemTaxAmount = (priceWithTax - priceWithoutTax) * quantity  // مالیات این آیتم
        const itemTotal = priceWithTax * quantity  // قیمت با مالیات × تعداد
        
        // Add to totals
        subtotal += itemSubtotal
        totalTax += itemTaxAmount
        
        // Display item line
        content += `
${item.name}
${quantity} × ${priceWithTax.toLocaleString('fa-IR')} = ${itemTotal.toLocaleString('fa-IR')} ریال
`
        
        // Show tax rate if item has tax
        if (vatRate > 0) {
          content += `  (مالیات ${vatRate}%)
`
        }
      })
    }

    // Grand total = subtotal + totalTax
    const grandTotal = subtotal + totalTax

    content += `
--------------------------------
جمع کالاها: ${Math.round(subtotal).toLocaleString('fa-IR')} ریال
مالیات: ${Math.round(totalTax).toLocaleString('fa-IR')} ریال
--------------------------------
جمع کل: ${Math.round(grandTotal).toLocaleString('fa-IR')} ریال

================================
       سپاسگزاریم
================================
`

    return content
  },

  // Browser fallback printing
  async printViaBrowser(receiptData) {
    return new Promise((resolve) => {
      const customer = receiptData.customer
      const content = this.generateReceiptContent(customer)
      
      // Create print window
      const printWindow = window.open('', '_blank', 'width=400,height=600')
      
      printWindow.document.write(`
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
          <meta charset="UTF-8">
          <title>فاکتور - Receipt</title>
          <style>
            body {
              font-family: 'Tahoma', Arial, sans-serif;
              font-size: 12px;
              line-height: 1.4;
              margin: 20px;
              direction: rtl;
              text-align: center;
            }
            .receipt {
              white-space: pre-line;
              max-width: 300px;
              margin: 0 auto;
            }
            @media print {
              body { margin: 0; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div class="receipt">${content}</div>
          <div class="no-print" style="margin-top: 20px;">
            <button onclick="window.print()">چاپ</button>
            <button onclick="window.close()">بستن</button>
          </div>
        </body>
        </html>
      `)
      
      printWindow.document.close()
      
      // Auto print after a short delay
      setTimeout(() => {
        printWindow.print()
        resolve({ success: true, message: 'Browser print initiated' })
      }, 500)
    })
  }
}

export default printerService
