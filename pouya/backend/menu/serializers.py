from rest_framework import serializers
from .models import Category, MenuItem, DailyInventory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_inventory = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    class Meta:
        model = MenuItem
        fields = '__all__'

    def get_price(self, obj):
        return obj.price_with_tax

    def get_current_inventory(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        try:
            inventory = obj.daily_inventory.get(date=today)
            return inventory.quantity_available
        except DailyInventory.DoesNotExist:
            return 0


class DailyInventorySerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = DailyInventory
        fields = '__all__'


class MenuItemWithInventorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_inventory = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'price_without_tax', 'price_with_tax', 
                 'vat_rate', 'category', 'category_name', 'image', 'is_available', 'current_inventory']

    def get_price(self, obj):
        return obj.price_with_tax

    def get_current_inventory(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        try:
            inventory = obj.daily_inventory.get(date=today)
            return inventory.quantity_available
        except DailyInventory.DoesNotExist:
            return 0 