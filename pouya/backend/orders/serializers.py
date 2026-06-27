from rest_framework import serializers
from .models import Order, OrderItem, Table
from menu.serializers import MenuItemSerializer
from menu.models import MenuItem


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    table_details = TableSerializer(source='table', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_items_count(self, obj):
        return obj.items.count()


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'notes', 'table', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data, created_by=self.context['request'].user)
        
        total_amount = 0
        for item_data in items_data:
            menu_item_id = item_data.get('menu_item_id')
            quantity = item_data.get('quantity', 1)
            notes = item_data.get('notes', '')
            
            try:
                menu_item = MenuItem.objects.get(id=menu_item_id)
                order_item = OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    notes=notes
                )
                total_amount += order_item.total_price
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError(f"Menu item with id {menu_item_id} does not exist")
        
        order.total_amount = total_amount
        order.save()
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'notes', 'status', 'table', 'items']

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update items if provided
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            total_amount = 0
            for item_data in items_data:
                menu_item_id = item_data.get('menu_item_id')
                quantity = item_data.get('quantity', 1)
                notes = item_data.get('notes', '')
                
                try:
                    menu_item = MenuItem.objects.get(id=menu_item_id)
                    order_item = OrderItem.objects.create(
                        order=instance,
                        menu_item=menu_item,
                        quantity=quantity,
                        notes=notes
                    )
                    total_amount += order_item.total_price
                except MenuItem.DoesNotExist:
                    raise serializers.ValidationError(f"Menu item with id {menu_item_id} does not exist")
            
            instance.total_amount = total_amount
        
        instance.save()
        return instance