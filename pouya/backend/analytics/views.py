"""Admin-only analytics endpoints: statistics + predictions."""
from rest_framework.views import APIView
from rest_framework.response import Response

from users.permissions import IsAdmin
from . import services


def _int_param(request, name, default, lo, hi):
    try:
        value = int(request.query_params.get(name, default))
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, value))


class StatisticsView(APIView):
    """GET /api/analytics/statistics/?days=30"""
    permission_classes = [IsAdmin]

    def get(self, request):
        days = _int_param(request, 'days', 30, 1, 365)
        return Response(services.get_statistics(days=days))


class PredictionsView(APIView):
    """GET /api/analytics/predictions/?horizon=7"""
    permission_classes = [IsAdmin]

    def get(self, request):
        horizon = _int_param(request, 'horizon', 7, 1, 30)
        return Response(services.get_predictions(horizon=horizon))
