#!/usr/bin/env python3
"""
Landscape Thermal Printer for Persian Receipts
Enhanced with Persian text support, Jalali calendar, and auto-cutter
"""

import os
import tempfile
import subprocess
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import jdatetime
import win32print
from bidi.algorithm import get_display
import arabic_reshaper


class ThermalReceiptPrinter:
    def __init__(self):
        # Receipt dimensions (portrait orientation for thermal printer)
        self.receipt_width = 300  # 80mm thermal printer width
        self.receipt_height = 800  # Dynamic height based on content
        
        # Font sizes (optimized for 80mm width)
        self.font_size_large = 24
        self.font_size_medium = 18
        self.font_size_small = 14
        
        # Layout settings
        self.line_spacing = 8
        self.margin = 0
        
        print("✅ ThermalReceiptPrinter initialized")

    def _load_persian_font(self, size):
        """Load Persian-compatible font with Vazir preference"""
        # Get current directory for local fonts
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        font_paths = [
            # Local Vazir fonts (in project)
            os.path.join(current_dir, "frontend", "src", "assets", "fonts", "Vazir-Bold.ttf"),
            os.path.join(current_dir, "frontend", "src", "assets", "fonts", "Vazir-Regular.ttf"),
            os.path.join(current_dir, "frontend", "src", "assets", "fonts", "Vazir-Medium.ttf"),
            # System Vazir fonts
            "C:/Windows/Fonts/Vazir-Bold.ttf",     # Vazir Bold (system)
            "C:/Windows/Fonts/Vazir.ttf",          # Vazir Regular (system)
            # Fallback fonts
            "C:/Windows/Fonts/tahomabd.ttf",       # Tahoma Bold
            "C:/Windows/Fonts/arialbd.ttf",        # Arial Bold
            "C:/Windows/Fonts/calibrib.ttf",       # Calibri Bold
            "C:/Windows/Fonts/tahoma.ttf",         # Tahoma Regular
            "C:/Windows/Fonts/arial.ttf",          # Arial Regular
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception as e:
                    print(f"⚠️ Failed to load {font_path}: {e}")
                    continue
        
        print("⚠️ Using default font")
        return ImageFont.load_default()

    def _fix_persian_text(self, text):
        """Fix Persian text direction and character shaping"""
        try:
            # Reshape Arabic/Persian characters
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"⚠️ Persian text fix failed: {e}")
            return text

    def _to_persian_digits(self, text):
        """Convert English digits to Persian digits"""
        persian_digits = '۰۱۲۳۴۵۶۷۸۹'
        english_digits = '0123456789'
        
        for i, eng_digit in enumerate(english_digits):
            text = text.replace(eng_digit, persian_digits[i])
        
        return text

    def _get_jalali_date_time(self):
        """Get current date and time in Jalali calendar"""
        try:
            jalali_now = jdatetime.datetime.now()
            
            # Persian month names
            persian_months = [
                'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
            ]
            
            # Format date and time
            jalali_date = self._to_persian_digits(jalali_now.strftime('%Y/%m/%d'))
            jalali_time = self._to_persian_digits(jalali_now.strftime('%H:%M'))
            
            # Beautiful date format
            month_name = persian_months[jalali_now.month - 1]
            day = self._to_persian_digits(str(jalali_now.day))
            year = self._to_persian_digits(str(jalali_now.year))
            jalali_date_beautiful = f"{day} {month_name} {year}"
            
            return {
                'date': jalali_date,
                'time': jalali_time,
                'date_beautiful': jalali_date_beautiful,
                'year': year,
                'month': month_name,
                'day': day
            }
        except Exception as e:
            print(f"⚠️ Jalali date conversion failed: {e}")
            # Fallback to Gregorian
            now = datetime.now()
            return {
                'date': now.strftime('%Y/%m/%d'),
                'time': now.strftime('%H:%M'),
                'date_beautiful': now.strftime('%Y/%m/%d'),
                'year': str(now.year),
                'month': str(now.month),
                'day': str(now.day)
            }

    def _draw_text_line(self, draw, text, x, y, font, bold_effect=False):
        """Draw text with optional bold effect"""
        if bold_effect:
            # Create bold effect by drawing text multiple times with slight offsets
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
            for dx, dy in offsets:
                draw.text((x + dx, y + dy), text, font=font, fill='black')
        else:
            draw.text((x, y), text, font=font, fill='black')

    def _draw_separator(self, draw, y, bold_effect=False):
        """Draw a separator line"""
        separator_text = "=" * 28
        font = self._load_persian_font(self.font_size_small)
        
        # Center the separator
        bbox = draw.textbbox((0, 0), separator_text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.receipt_width - text_width) // 2
        
        self._draw_text_line(draw, separator_text, x, y, font, bold_effect)
        return y + self.line_spacing + 10

    def create_portrait_receipt(self, customer_data):
        """Create a portrait receipt image with Persian support"""
        try:
            # Create image with white background
            img = Image.new('RGB', (self.receipt_width, self.receipt_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Load fonts
            font_large = self._load_persian_font(self.font_size_large)
            font_medium = self._load_persian_font(self.font_size_medium)
            font_small = self._load_persian_font(self.font_size_small)
            
            # Starting position
            y_pos = 10  # Minimal top margin
            
            # Restaurant header (centered, bold) - Persian only
            header_persian = self._fix_persian_text("پویا")
            
            # Center Persian header
            bbox = draw.textbbox((0, 0), header_persian, font=font_large)
            text_width = bbox[2] - bbox[0]
            x_center = (self.receipt_width - text_width) // 2
            self._draw_text_line(draw, header_persian, x_center, y_pos, font_large, bold_effect=True)
            y_pos += self.font_size_large + self.line_spacing
            
            # Separator
            y_pos = self._draw_separator(draw, y_pos, bold_effect=True)
            
            # Get Jalali date and time
            jalali_info = self._get_jalali_date_time()
            
            # Order information (two columns)
            order_num = customer_data.get('orderNumber', 'N/A')
            customer_name = customer_data.get('name', 'مشتری')
            customer_phone = customer_data.get('phone', '')
            
            # Order information (Persian only, centered)
            info_texts = [
                self._fix_persian_text(f"شماره سفارش: {order_num}"),
                self._fix_persian_text(f"تاریخ: {jalali_info['date_beautiful']}"),
                self._fix_persian_text(f"ساعت: {jalali_info['time']}"),
                self._fix_persian_text(f"مشتری: {customer_name}"),
            ]
            
            if customer_phone:
                info_texts.append(self._fix_persian_text(f"تلفن: {customer_phone}"))
            
            # Draw centered information
            for text in info_texts:
                bbox = draw.textbbox((0, 0), text, font=font_small)
                text_width = bbox[2] - bbox[0]
                x_center = (self.receipt_width - text_width) // 2
                self._draw_text_line(draw, text, x_center, y_pos, font_small, bold_effect=True)
                y_pos += self.font_size_small + self.line_spacing
            
            # Items separator
            y_pos = self._draw_separator(draw, y_pos, bold_effect=True)
            
            # Order items header
            items_header = self._fix_persian_text("لیست خرید")
            bbox = draw.textbbox((0, 0), items_header, font=font_medium)
            text_width = bbox[2] - bbox[0]
            x_center = (self.receipt_width - text_width) // 2
            self._draw_text_line(draw, items_header, x_center, y_pos, font_medium, bold_effect=True)
            y_pos += self.font_size_medium + self.line_spacing * 2
            
            # Order items (simple list format)
            total_amount = 0
            items = customer_data.get('items', [])
            
            for item in items:
                item_name = self._fix_persian_text(item.get('name', 'آیتم نامشخص'))
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                item_total = quantity * price
                total_amount += item_total
                
                # Item name (centered)
                bbox = draw.textbbox((0, 0), item_name, font=font_small)
                text_width = bbox[2] - bbox[0]
                x_center = (self.receipt_width - text_width) // 2
                self._draw_text_line(draw, item_name, x_center, y_pos, font_small, bold_effect=True)
                y_pos += self.font_size_small + self.line_spacing
                
                # Quantity and price line (centered)
                quantity_persian = self._to_persian_digits(str(quantity))
                price_persian = self._to_persian_digits(f"{price:,.0f}")
                total_persian = self._to_persian_digits(f"{item_total:,.0f}")
                
                price_line = self._fix_persian_text(f"{quantity_persian} × {price_persian} = {total_persian} تومان")
                bbox = draw.textbbox((0, 0), price_line, font=font_small)
                text_width = bbox[2] - bbox[0]
                x_center = (self.receipt_width - text_width) // 2
                self._draw_text_line(draw, price_line, x_center, y_pos, font_small)
                y_pos += self.font_size_small + self.line_spacing * 2
            
            # Total separator
            y_pos = self._draw_separator(draw, y_pos, bold_effect=True)
            
            # Total amount (Persian only)
            total_persian = self._to_persian_digits(f"{total_amount:,.0f}")
            total_text = self._fix_persian_text(f"جمع کل: {total_persian} تومان")
            bbox = draw.textbbox((0, 0), total_text, font=font_large)
            text_width = bbox[2] - bbox[0]
            x_center = (self.receipt_width - text_width) // 2
            self._draw_text_line(draw, total_text, x_center, y_pos, font_large, bold_effect=True)
            y_pos += self.font_size_large + self.line_spacing
            
            # Final separator
            y_pos = self._draw_separator(draw, y_pos, bold_effect=True)
            
            # Thank you message (Persian only)
            thank_you_persian = self._fix_persian_text("سپاسگزاریم")
            bbox = draw.textbbox((0, 0), thank_you_persian, font=font_medium)
            text_width = bbox[2] - bbox[0]
            x_center = (self.receipt_width - text_width) // 2
            self._draw_text_line(draw, thank_you_persian, x_center, y_pos, font_medium, bold_effect=True)
            y_pos += self.font_size_medium + self.line_spacing
            
            # Final separator
            y_pos = self._draw_separator(draw, y_pos, bold_effect=True)
            
            # Crop image to actual content height with minimal bottom margin
            final_height = y_pos + 10
            img = img.crop((0, 0, self.receipt_width, final_height))
            
            print("✅ Receipt image created successfully")
            return img
            
        except Exception as e:
            print(f"❌ Error creating receipt image: {e}")
            raise

    def _send_cutter_command(self):
        """Send auto-cutter command to thermal printer (single cut only)"""
        try:
            import time
            
            # Small delay to ensure print job is complete
            time.sleep(1)
            
            default_printer = win32print.GetDefaultPrinter()
            printer_handle = win32print.OpenPrinter(default_printer)
            
            # Single cutter command (simplified to avoid double cutting)
            cutter_command = b'\x1D\x56\x00'  # GS V 0 - Partial cut (gentler)
            
            job_info = ("Cutter Command", None, None)
            job_id = win32print.StartDocPrinter(printer_handle, 1, job_info)
            win32print.StartPagePrinter(printer_handle)
            
            # Send single cutter command
            win32print.WritePrinter(printer_handle, cutter_command)
            
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
            win32print.ClosePrinter(printer_handle)
            
            print("✅ Single cutter command sent successfully")
            
        except Exception as e:
            print(f"⚠️ Cutter command failed: {e}")
            # Don't raise exception, just log the error
            pass

    def print_portrait_image(self, img):
        """Print image using Windows image printing with auto-cutter"""
        try:
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name, 'PNG')
                temp_path = tmp_file.name
            
            try:
                # Method 1: Try PowerShell with portrait settings
                powershell_cmd = f'''
                Add-Type -AssemblyName System.Drawing
                Add-Type -AssemblyName System.Windows.Forms
                $img = [System.Drawing.Image]::FromFile("{temp_path}")
                $pd = New-Object System.Drawing.Printing.PrintDocument
                $pd.PrinterSettings.PrinterName = [System.Drawing.Printing.PrinterSettings]::new().PrinterName
                $pd.DefaultPageSettings.Landscape = $false
                $pd.DefaultPageSettings.Margins = New-Object System.Drawing.Printing.Margins(0,0,0,0)
                $pd.add_PrintPage({{
                    $pageWidth = $_.PageBounds.Width
                    $pageHeight = $_.PageBounds.Height
                    $imgWidth = $img.Width
                    $imgHeight = $img.Height
                    $x = [math]::Max(0, ($pageWidth - $imgWidth) / 2)
                    $y = 0
                    $_.Graphics.DrawImage($img, $x, $y, $imgWidth, $imgHeight)
                }})
                $pd.Print()
                $img.Dispose()
                '''
                
                result = subprocess.run(['powershell', '-Command', powershell_cmd], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("✅ Image printed successfully via PowerShell")
                    return True
                else:
                    print(f"⚠️ PowerShell print failed: {result.stderr}")
                    
            except Exception as e:
                print(f"⚠️ PowerShell method failed: {e}")
            
            # Method 2: Fallback to MSPaint
            try:
                subprocess.run(['mspaint', '/p', temp_path], timeout=30)
                print("✅ Image printed successfully via MSPaint")
                return True
                
            except Exception as e:
                print(f"⚠️ MSPaint method failed: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Print failed: {e}")
            return False
        finally:
            # Clean up temporary file
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except Exception as e:
                print(f"⚠️ Failed to delete temp file: {e}")

    def print_receipt(self, customer_data):
        """Main method to print customer receipt"""
        try:
            print("🖨️ Starting receipt printing...")
            print(f"Customer: {customer_data.get('name', 'Unknown')}")
            print(f"Order: {customer_data.get('orderNumber', 'N/A')}")
            
            # Create receipt image
            img = self.create_portrait_receipt(customer_data)
            
            # Print the image
            success = self.print_portrait_image(img)
            
            if success:
                # Send cutter command only once after successful print
                self._send_cutter_command()
                print("✅ Receipt printed successfully!")
                return {"success": True, "message": "فاکتور با موفقیت چاپ شد"}
            else:
                print("❌ Receipt printing failed!")
                return {"success": False, "error": "خطا در چاپ فاکتور"}
                
        except Exception as e:
            print(f"❌ Receipt printing error: {e}")
            return {"success": False, "error": f"خطا در چاپ: {str(e)}"}

    def test_printer(self):
        """Test printer with sample data"""
        test_data = {
            'name': 'علی احمدی',
            'phone': '۰۹۱۲۳۴۵۶۷۸۹',
            'orderNumber': 'ORD-۱۴۰۳۰۹۲۶-۰۰۱',
            'items': [
                {'name': 'چلو کباب کوبیده', 'quantity': 2, 'price': 250000},
                {'name': 'نوشابه', 'quantity': 1, 'price': 15000},
            ]
        }
        
        return self.print_receipt(test_data)


if __name__ == "__main__":
    printer = ThermalReceiptPrinter()
    result = printer.test_printer()
    print(f"Test result: {result}")
