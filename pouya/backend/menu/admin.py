from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Category, MenuItem, DailyInventory


# Resource classes for import/export
class CategoryResource(resources.ModelResource):
    name = fields.Field(column_name='نام دسته‌بندی', attribute='name')
    description = fields.Field(column_name='توضیحات', attribute='description')
    created_at = fields.Field(column_name='تاریخ ایجاد', attribute='created_at')
    updated_at = fields.Field(column_name='تاریخ بروزرسانی', attribute='updated_at')
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        export_order = ('id', 'name', 'description', 'created_at', 'updated_at')


class MenuItemResource(resources.ModelResource):
    name = fields.Field(column_name='نام غذا', attribute='name')
    product_code = fields.Field(column_name='کد محصول', attribute='product_code')
    category__name = fields.Field(column_name='دسته‌بندی', attribute='category__name')
    description = fields.Field(column_name='توضیحات', attribute='description')
    price_without_tax = fields.Field(column_name='قیمت بدون مالیات', attribute='price_without_tax')
    vat_rate = fields.Field(column_name='نرخ مالیات بر ارزش افزوده', attribute='vat_rate')
    price_with_tax = fields.Field(column_name='قیمت با مالیات', attribute='price_with_tax')
    is_available = fields.Field(column_name='موجود است', attribute='is_available')
    is_active = fields.Field(column_name='فعال است', attribute='is_active')
    created_at = fields.Field(column_name='تاریخ ایجاد', attribute='created_at')
    updated_at = fields.Field(column_name='تاریخ بروزرسانی', attribute='updated_at')
    
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'product_code', 'category__name', 'description', 
                  'price_without_tax', 'vat_rate', 'price_with_tax', 'is_available', 'is_active', 
                  'created_at', 'updated_at')
        export_order = ('id', 'name', 'product_code', 'category__name', 
                        'price_without_tax', 'vat_rate', 'price_with_tax', 'is_available', 
                        'is_active', 'created_at', 'updated_at')


class DailyInventoryResource(resources.ModelResource):
    menu_item__name = fields.Field(column_name='نام غذا', attribute='menu_item__name')
    menu_item__product_code = fields.Field(column_name='کد محصول', attribute='menu_item__product_code')
    quantity_available = fields.Field(column_name='موجودی', attribute='quantity_available')
    date = fields.Field(column_name='تاریخ', attribute='date')
    created_at = fields.Field(column_name='تاریخ ایجاد', attribute='created_at')
    updated_at = fields.Field(column_name='تاریخ بروزرسانی', attribute='updated_at')
    
    class Meta:
        model = DailyInventory
        fields = ('id', 'menu_item__name', 'menu_item__product_code', 
                  'quantity_available', 'date', 'created_at', 'updated_at')
        export_order = ('id', 'menu_item__name', 'menu_item__product_code', 
                        'quantity_available', 'date', 'created_at', 'updated_at')


# Admin classes with import/export functionality
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(ImportExportModelAdmin):
    resource_class = MenuItemResource
    list_display = ['name', 'product_code', 'category', 'price_without_tax', 'vat_rate', 'price_with_tax', 'is_available', 'created_at']
    list_filter = ['category', 'vat_rate', 'is_available', 'is_active', 'created_at']
    search_fields = ['name', 'product_code', 'description']
    ordering = ['category', 'name']
    readonly_fields = ['price_with_tax']


@admin.register(DailyInventory)
class DailyInventoryAdmin(ImportExportModelAdmin):
    resource_class = DailyInventoryResource
    list_display = ['menu_item', 'quantity_available', 'date', 'created_at']
    list_filter = ['date', 'menu_item__category']
    search_fields = ['menu_item__name']
    ordering = ['-date', 'menu_item__name']
