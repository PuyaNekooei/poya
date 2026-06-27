from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from users.permissions import IsAdminOrChef, IsAdminOrReadOnly
from .models import Category, MenuItem, DailyInventory
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    DailyInventorySerializer,
    MenuItemWithInventorySerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.filter(is_available=True)

    @action(detail=False, methods=['get'])
    def with_inventory(self, request):
        """Get menu items with current day's inventory"""
        today = timezone.now().date()
        menu_items = MenuItem.objects.filter(is_available=True)
        
        # Add inventory information
        for item in menu_items:
            try:
                inventory = item.daily_inventory.get(date=today)
                item.current_inventory = inventory.quantity_available
            except DailyInventory.DoesNotExist:
                item.current_inventory = 0
        
        serializer = MenuItemWithInventorySerializer(menu_items, many=True)
        return Response(serializer.data)


class DailyInventoryViewSet(viewsets.ModelViewSet):
    queryset = DailyInventory.objects.all()
    serializer_class = DailyInventorySerializer
    permission_classes = [IsAdminOrChef]

    def get_queryset(self):
        queryset = DailyInventory.objects.all()
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)
        else:
            # Default to today
            today = timezone.now().date()
            queryset = queryset.filter(date=today)
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update inventory for multiple items"""
        inventory_data = request.data.get('inventory', [])
        date = request.data.get('date', timezone.now().date())
        
        updated_items = []
        for item_data in inventory_data:
            menu_item_id = item_data.get('menu_item_id')
            quantity = item_data.get('quantity', 0)
            
            try:
                menu_item = MenuItem.objects.get(id=menu_item_id)
                inventory, created = DailyInventory.objects.get_or_create(
                    menu_item=menu_item,
                    date=date,
                    defaults={'quantity_available': quantity}
                )
                if not created:
                    inventory.quantity_available = quantity
                    inventory.save()
                
                updated_items.append({
                    'menu_item_id': menu_item_id,
                    'menu_item_name': menu_item.name,
                    'quantity_available': inventory.quantity_available
                })
            except MenuItem.DoesNotExist:
                return Response(
                    {'error': f'Menu item with id {menu_item_id} does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response({
            'message': f'Inventory updated for {len(updated_items)} items',
            'updated_items': updated_items
        })
