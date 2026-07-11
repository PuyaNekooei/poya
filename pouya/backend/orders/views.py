from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from users.permissions import IsOrderStaff, IsAdminOrReadOnly, IsOrderViewer
from .models import Order, OrderItem, Table
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderItemSerializer,
    TableSerializer
)


class TableViewSet(viewsets.ModelViewSet):
    """Dine-in tables. Everyone authenticated can read; only admins can edit."""
    queryset = Table.objects.all().order_by('number')
    serializer_class = TableSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Table.objects.all().order_by('number')
        active = self.request.query_params.get('active', None)
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() in ('1', 'true', 'yes'))
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsOrderStaff]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        # The customer-facing status board is read-only and also open to the
        # 'customer' role; every other action stays staff-only.
        if self.action == 'status_board':
            return [IsOrderViewer()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Order.objects.all().order_by('-created_at')
        status_filter = self.request.query_params.get('status', None)
        date_filter = self.request.query_params.get('date', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if date_filter:
            queryset = queryset.filter(created_at__date=date_filter)
        
        return queryset

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's orders"""
        today = timezone.localdate()
        orders = Order.objects.filter(created_at__date=today).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders"""
        orders = Order.objects.filter(status='pending').order_by('created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        # Get valid status choices
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        
        if new_status not in valid_statuses:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def status_board(self, request):
        """Slim, read-only list of today's orders and their status.

        Used by the customer-facing status page and the dashboard status panel.
        Returns only the fields needed to display status (no prices/items)."""
        today = timezone.localdate()
        orders = Order.objects.filter(created_at__date=today).order_by('-created_at')
        data = [{
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.customer_name,
            'status': order.status,
            'status_display': order.get_status_display(),
            'table_number': order.table.number if order.table else None,
            'created_at': order.created_at,
        } for order in orders]
        return Response(data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get order statistics"""
        today = timezone.localdate()
        
        today_orders = Order.objects.filter(created_at__date=today)
        total_orders = today_orders.count()
        total_revenue = sum(order.total_amount for order in today_orders)
        
        status_counts = {}
        for status_choice in Order.ORDER_STATUS_CHOICES:
            status_counts[status_choice[0]] = today_orders.filter(status=status_choice[0]).count()
        
        return Response({
            'today_orders': total_orders,
            'today_revenue': total_revenue,
            'status_breakdown': status_counts
        })


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsOrderStaff]

    def get_queryset(self):
        queryset = OrderItem.objects.all()
        order_id = self.request.query_params.get('order', None)
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset
