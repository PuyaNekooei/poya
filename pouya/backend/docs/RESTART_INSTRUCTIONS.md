# How to Apply Export Header Changes

## The Problem
Django admin caches Python modules, so changes to admin.py files won't take effect until you properly restart.

## Solution: Complete Restart Steps

### Option 1: If Running Django Development Server

1. **Stop the server completely**:
   - Press `Ctrl + C` in the terminal where Django is running
   - Wait for it to fully stop

2. **Clear Python cache** (optional but recommended):
   ```powershell
   cd D:\Projects\yas\backend
   Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
   Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Force -Recurse
   ```

3. **Restart Django**:
   ```powershell
   cd D:\Projects\yas\backend
   venv\Scripts\python.exe manage.py runserver
   ```

4. **Clear browser cache**:
   - Press `Ctrl + Shift + R` to hard refresh in your browser
   - Or open Django admin in an incognito/private window

### Option 2: If Running as Windows Service

1. **Stop the service**:
   ```powershell
   cd D:\Projects\yas\backend
   .\manage_nssm_service.bat
   # Choose option to stop the service
   ```

2. **Clear Python cache**:
   ```powershell
   Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
   Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Force -Recurse
   ```

3. **Start the service**:
   ```powershell
   .\manage_nssm_service.bat
   # Choose option to start the service
   ```

4. **Clear browser cache** and visit admin again

### Option 3: Nuclear Option (Complete Reset)

If the above doesn't work:

```powershell
# 1. Kill all Python processes
Get-Process python* | Stop-Process -Force

# 2. Navigate to backend
cd D:\Projects\yas\backend

# 3. Clear ALL cache
Get-ChildItem -Recurse -Filter "*.pyc" -Force | Remove-Item -Force
Get-ChildItem -Recurse -Filter "__pycache__" -Force | Remove-Item -Force -Recurse

# 4. Restart Django
venv\Scripts\python.exe manage.py runserver
```

## Verify It's Working

1. Go to Django Admin: `http://127.0.0.1:8000/admin/`
2. Navigate to **Menu → Menu Items**
3. Click the **Export** button (top right)
4. Select **XLSX** format
5. Check the downloaded file - headers should be in Persian

## Expected Headers

### Menu Items (منو):
- نام غذا (Name)
- کد محصول (Product Code)
- دسته‌بندی (Category)
- قیمت بدون مالیات (Price Without Tax)
- نرخ مالیات بر ارزش افزوده (VAT Rate)
- قیمت با مالیات (Price With Tax)

### Orders (سفارش‌ها):
- شماره سفارش (Order Number)
- نام مشتری (Customer Name)
- مبلغ کل (Total Amount)
- وضعیت (Status)

## Still Not Working?

If headers are still in English after following all steps above:

1. **Check if files were saved**:
   ```powershell
   cat backend\menu\admin.py | Select-String "column_name"
   ```
   You should see Persian text.

2. **Check Django is loading your app**:
   - Look at Django startup logs
   - Ensure no errors about import_export

3. **Verify import_export is installed**:
   ```powershell
   venv\Scripts\pip.exe show django-import-export
   ```

4. **Try exporting from a different model** (Orders, Menu Items, etc.) to see if the issue is specific to one model.

## Contact for Help

If none of the above works, there might be:
- A conflicting plugin/package
- A different version of django-import-export
- Browser caching issues (try different browser)



