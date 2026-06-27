"""
Statistics and (simple statistical) forecasting for the restaurant.

No ML dependencies — forecasting blends weekday seasonality with a recent
moving average, which is robust with limited data and fully explainable.

All functions return plain JSON-serialisable dicts (floats/ints/strings).
"""
from datetime import timedelta
import math

import jdatetime
import pandas as pd
from django.utils import timezone

from orders.models import Order, OrderItem
from menu.models import DailyInventory

# How much history to look at when learning patterns for predictions.
HISTORY_DAYS = 90
# Blend weight between weekday-average and recent moving average.
WEEKDAY_WEIGHT = 0.5


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _tz():
    return timezone.get_current_timezone()


def _jalali(d):
    """ISO date -> Jalali 'YYYY/MM/DD' string for display."""
    jd = jdatetime.date.fromgregorian(date=d)
    return jd.strftime('%Y/%m/%d')


def _orders_df():
    """Non-cancelled orders as a DataFrame with local date/hour/weekday."""
    cols = ['id', 'created_at', 'total_amount', 'order_type',
            'table__number', 'table__name']
    rows = list(Order.objects.exclude(status='cancelled').values(*cols))
    if not rows:
        return pd.DataFrame(columns=cols + ['total_amount', 'date', 'hour', 'weekday'])
    df = pd.DataFrame(rows)
    df['total_amount'] = df['total_amount'].astype(float)
    local = pd.to_datetime(df['created_at'], utc=True).dt.tz_convert(_tz())
    df['date'] = local.dt.date
    df['hour'] = local.dt.hour
    df['weekday'] = local.dt.weekday  # Monday=0 .. Sunday=6
    return df


def _items_df():
    """Non-cancelled order items as a DataFrame, with a resolved item name."""
    cols = ['quantity', 'total_price', 'menu_item_id', 'menu_item__name',
            'menu_item__category__name', 'product_info', 'order__created_at']
    rows = list(OrderItem.objects.exclude(order__status='cancelled').values(*cols))
    if not rows:
        return pd.DataFrame(columns=['quantity', 'total_price', 'menu_item_id',
                                     'name', 'category', 'date', 'weekday'])
    df = pd.DataFrame(rows)
    df['quantity'] = df['quantity'].astype(int)
    df['total_price'] = df['total_price'].astype(float)

    def name_of(row):
        if row['menu_item__name']:
            return row['menu_item__name']
        info = row['product_info'] or {}
        return info.get('product_name', 'نامشخص')

    df['name'] = df.apply(name_of, axis=1)
    df['category'] = df['menu_item__category__name'].fillna('بدون دسته‌بندی')
    local = pd.to_datetime(df['order__created_at'], utc=True).dt.tz_convert(_tz())
    df['date'] = local.dt.date
    df['weekday'] = local.dt.weekday
    return df


def _filled_daily(df, value_aggs, today):
    """Daily aggregate reindexed to a gap-free date range (missing days -> 0)."""
    if df.empty:
        return pd.DataFrame()
    daily = df.groupby('date').agg(**value_aggs)
    full = pd.date_range(min(df['date']), today, freq='D').date
    daily = daily.reindex(full, fill_value=0)
    daily.index.name = 'date'
    return daily


# --------------------------------------------------------------------------- #
# Statistics
# --------------------------------------------------------------------------- #
def get_statistics(days=30):
    df = _orders_df()
    idf = _items_df()
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    start = today - timedelta(days=days - 1)

    if df.empty:
        return {
            'has_data': False, 'days': days,
            'range': {'start': start.isoformat(), 'end': today.isoformat()},
            'kpis': {}, 'revenue_trend': [], 'top_items': [],
            'by_hour': [], 'by_status': {}, 'by_type': {}, 'by_table': [],
        }

    in_range = df[df['date'] >= start]

    def rev(frame):
        return float(frame['total_amount'].sum())

    today_rows = df[df['date'] == today]
    yest_rows = df[df['date'] == yesterday]

    # --- KPIs ---
    range_revenue = rev(in_range)
    range_orders = int(len(in_range))
    kpis = {
        'today_revenue': round(rev(today_rows)),
        'today_orders': int(len(today_rows)),
        'yesterday_revenue': round(rev(yest_rows)),
        'yesterday_orders': int(len(yest_rows)),
        'range_revenue': round(range_revenue),
        'range_orders': range_orders,
        'avg_order_value': round(range_revenue / range_orders) if range_orders else 0,
        'avg_daily_revenue': round(range_revenue / days),
    }

    # --- Revenue & orders trend (gap-free) ---
    daily = _filled_daily(in_range, {'revenue': ('total_amount', 'sum'),
                                     'orders': ('id', 'count')}, today)
    daily = daily[daily.index >= start]
    revenue_trend = [{
        'date': d.isoformat(),
        'jdate': _jalali(d),
        'revenue': round(float(row['revenue'])),
        'orders': int(row['orders']),
    } for d, row in daily.iterrows()]

    # --- Top selling items ---
    top_items = []
    if not idf.empty:
        items_range = idf[idf['date'] >= start]
        if not items_range.empty:
            grouped = (items_range.groupby('name')
                       .agg(quantity=('quantity', 'sum'),
                            revenue=('total_price', 'sum'),
                            category=('category', 'first'))
                       .sort_values('quantity', ascending=False).head(15))
            top_items = [{
                'name': name,
                'category': row['category'],
                'quantity': int(row['quantity']),
                'revenue': round(float(row['revenue'])),
            } for name, row in grouped.iterrows()]

    # --- Orders by hour ---
    by_hour_counts = in_range.groupby('hour').agg(
        orders=('id', 'count'), revenue=('total_amount', 'sum'))
    by_hour = []
    for h in range(24):
        if h in by_hour_counts.index:
            r = by_hour_counts.loc[h]
            by_hour.append({'hour': h, 'orders': int(r['orders']),
                            'revenue': round(float(r['revenue']))})
        else:
            by_hour.append({'hour': h, 'orders': 0, 'revenue': 0})

    # --- By status (include cancelled) over range ---
    status_rows = Order.objects.filter(created_at__date__gte=start)
    by_status = {}
    for code, label in Order.ORDER_STATUS_CHOICES:
        by_status[code] = {'label': str(label),
                           'count': status_rows.filter(status=code).count()}

    # --- By type ---
    by_type = {
        'manual': int((in_range['order_type'] == 'manual').sum()),
    }

    # --- By table ---
    by_table = []
    tdf = in_range[in_range['table__number'].notna()]
    if not tdf.empty:
        grouped = (tdf.groupby('table__number')
                   .agg(orders=('id', 'count'),
                        revenue=('total_amount', 'sum'),
                        name=('table__name', 'first'))
                   .sort_values('orders', ascending=False))
        for number, row in grouped.iterrows():
            by_table.append({
                'table': int(number),
                'name': row['name'] or '',
                'orders': int(row['orders']),
                'revenue': round(float(row['revenue'])),
            })

    return {
        'has_data': True, 'days': days,
        'range': {'start': start.isoformat(), 'end': today.isoformat()},
        'kpis': kpis,
        'revenue_trend': revenue_trend,
        'top_items': top_items,
        'by_hour': by_hour,
        'by_status': by_status,
        'by_type': by_type,
        'by_table': by_table,
    }


# --------------------------------------------------------------------------- #
# Predictions (simple statistical: weekday seasonality + moving average)
# --------------------------------------------------------------------------- #
def _blend(weekday_mean, recent_mean):
    return WEEKDAY_WEIGHT * weekday_mean + (1 - WEEKDAY_WEIGHT) * recent_mean


def get_predictions(horizon=7):
    df = _orders_df()
    idf = _items_df()
    today = timezone.localdate()
    hist_start = today - timedelta(days=HISTORY_DAYS)

    df = df[df['date'] >= hist_start]
    idf = idf[idf['date'] >= hist_start] if not idf.empty else idf

    if df.empty:
        return {'has_data': False, 'horizon': horizon,
                'daily_sales_forecast': [], 'item_demand': [],
                'busy_hours': [], 'peak_hours': [], 'busiest_weekday': None,
                'restock_suggestions': [], 'history_days': 0}

    daily = _filled_daily(df, {'revenue': ('total_amount', 'sum'),
                               'orders': ('id', 'count')}, today)
    history_days = int(len(daily))
    daily['weekday'] = [d.weekday() for d in daily.index]

    wd_rev = daily.groupby('weekday')['revenue'].mean()
    wd_ord = daily.groupby('weekday')['orders'].mean()
    recent = daily.tail(7)
    recent_rev = float(recent['revenue'].mean())
    recent_ord = float(recent['orders'].mean())

    # --- Daily sales/revenue forecast ---
    daily_sales_forecast = []
    for i in range(1, horizon + 1):
        d = today + timedelta(days=i)
        wd = d.weekday()
        pr = _blend(float(wd_rev.get(wd, recent_rev)), recent_rev)
        po = _blend(float(wd_ord.get(wd, recent_ord)), recent_ord)
        daily_sales_forecast.append({
            'date': d.isoformat(), 'jdate': _jalali(d),
            'predicted_revenue': round(pr),
            'predicted_orders': int(round(po)),
        })

    # --- Per-item demand (next day + over horizon) ---
    item_demand, item_next_day = [], {}
    if not idf.empty:
        pivot = (idf.groupby(['date', 'name'])['quantity'].sum().unstack(fill_value=0)
                 .reindex(daily.index, fill_value=0))
        pivot_wd = pivot.copy()
        pivot_wd['weekday'] = [d.weekday() for d in pivot_wd.index]
        recent_item = pivot.tail(7).mean()
        wd_item = pivot_wd.groupby('weekday').mean()
        tomorrow_wd = (today + timedelta(days=1)).weekday()
        for name in pivot.columns:
            rec = float(recent_item.get(name, 0.0))
            wdm = float(wd_item.loc[tomorrow_wd, name]) if tomorrow_wd in wd_item.index else rec
            next_day = _blend(wdm, rec)
            # horizon = sum of per-day blended predictions
            horizon_total = 0.0
            for i in range(1, horizon + 1):
                wd = (today + timedelta(days=i)).weekday()
                wval = float(wd_item.loc[wd, name]) if wd in wd_item.index else rec
                horizon_total += _blend(wval, rec)
            item_next_day[name] = next_day
            item_demand.append({
                'name': name,
                'predicted_next_day': int(round(next_day)),
                'predicted_horizon': int(round(horizon_total)),
            })
        item_demand = [x for x in item_demand if x['predicted_horizon'] > 0]
        item_demand.sort(key=lambda x: x['predicted_horizon'], reverse=True)
        item_demand = item_demand[:20]

    # --- Busy hours (avg orders per active day) ---
    active_days = max(1, daily[daily['orders'] > 0].shape[0])
    hour_counts = df.groupby('hour')['id'].count()
    busy_hours = []
    for h in range(24):
        avg = float(hour_counts.get(h, 0)) / active_days
        busy_hours.append({'hour': h, 'avg_orders': round(avg, 2)})
    peak = sorted(busy_hours, key=lambda x: x['avg_orders'], reverse=True)
    peak_hours = [x['hour'] for x in peak[:3] if x['avg_orders'] > 0]
    for entry in busy_hours:
        entry['is_peak'] = entry['hour'] in peak_hours

    # --- Busiest weekday ---
    wd_names = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
    busiest_weekday = None
    if not wd_ord.empty and wd_ord.max() > 0:
        bw = int(wd_ord.idxmax())
        busiest_weekday = {'weekday': bw, 'name': wd_names[bw],
                           'avg_orders': round(float(wd_ord.max()), 2)}

    # --- Restock suggestions (predicted tomorrow vs today's inventory) ---
    restock = []
    if not idf.empty:
        linked = idf[idf['menu_item_id'].notna()]
        if not linked.empty:
            inv_today = {row['menu_item_id']: row['quantity_available']
                         for row in DailyInventory.objects.filter(date=today)
                         .values('menu_item_id', 'quantity_available')}
            # predicted next-day qty per menu_item_id
            pv = (linked.groupby(['date', 'menu_item_id'])['quantity'].sum()
                  .unstack(fill_value=0).reindex(daily.index, fill_value=0))
            pv_wd = pv.copy()
            pv_wd['weekday'] = [d.weekday() for d in pv_wd.index]
            recent_pv = pv.tail(7).mean()
            wd_pv = pv_wd.groupby('weekday').mean()
            tomorrow_wd = (today + timedelta(days=1)).weekday()
            # map id -> a display name
            id_name = (linked.groupby('menu_item_id')['name'].first().to_dict())
            for mid in pv.columns:
                rec = float(recent_pv.get(mid, 0.0))
                wdm = float(wd_pv.loc[tomorrow_wd, mid]) if tomorrow_wd in wd_pv.index else rec
                pred = _blend(wdm, rec)
                pred_q = int(math.ceil(pred))
                current = int(inv_today.get(mid, 0))
                if pred_q <= 0:
                    continue
                restock.append({
                    'menu_item_id': int(mid),
                    'name': id_name.get(mid, 'نامشخص'),
                    'predicted_next_day': pred_q,
                    'current_inventory': current,
                    'suggested_restock': max(0, pred_q - current),
                })
            restock.sort(key=lambda x: x['suggested_restock'], reverse=True)
            restock = restock[:20]

    return {
        'has_data': True,
        'horizon': horizon,
        'history_days': history_days,
        'daily_sales_forecast': daily_sales_forecast,
        'item_demand': item_demand,
        'busy_hours': busy_hours,
        'peak_hours': peak_hours,
        'busiest_weekday': busiest_weekday,
        'restock_suggestions': restock,
        'method': 'weekday-seasonality + 7-day moving average',
    }
