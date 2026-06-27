# -*- coding: utf-8 -*-
"""
Seed ~3 months of realistic sample orders for an Iranian restaurant.

The data is shaped to look like a real Persian eatery so the analytics &
prediction endpoints produce meaningful, sensible output:

  * Lunch is the main meal in Iran -> the midday peak is the biggest.
  * Thursday / Friday (Iranian weekend) are the busiest days.
  * Kababs (کوبیده، جوجه، برگ) and polo dishes are the best sellers,
    fast-food (pizza/burger) appeals to a smaller crowd, and most meals
    are ordered together with a soft drink or dough.
  * A few orders get cancelled; older orders are completed; today's orders
    are spread across the live statuses.

Usage:
    python manage.py seed_sample_data
    python manage.py seed_sample_data --days 90 --clear
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone

from menu.models import MenuItem, DailyInventory
from orders.models import Order, OrderItem, Table


# --------------------------------------------------------------------------- #
# Iranian flavour: names, weekday / hour seasonality, item popularity
# --------------------------------------------------------------------------- #
CUSTOMER_NAMES = [
    'علی رضایی', 'محمد حسینی', 'فاطمه احمدی', 'زهرا کریمی', 'حسین موسوی',
    'مریم نوری', 'رضا قاسمی', 'سارا جعفری', 'امیر محمدی', 'نگار صادقی',
    'مهدی عباسی', 'الهام رحیمی', 'سعید کاظمی', 'لیلا اکبری', 'بهنام فرهادی',
    'شیما یوسفی', 'پویا نجفی', 'مینا حیدری', 'کیان شریفی', 'آرش بهرامی',
    'نیلوفر مرادی', 'فرهاد سلطانی', 'پریسا اسدی', 'بابک زارعی', 'هانیه قربانی',
    'یاسر طاهری', 'سمیرا عزیزی', 'وحید ملکی', 'رویا امینی', 'کاوه داوری',
]

# Per-weekday order-count multiplier. Python weekday(): Mon=0 .. Sun=6.
# Iranian weekend = Thursday(3) + Friday(4); Friday is the big family-meal day.
WEEKDAY_MULTIPLIER = {
    0: 0.95,  # دوشنبه  Monday
    1: 0.90,  # سه‌شنبه Tuesday
    2: 1.00,  # چهارشنبه Wednesday
    3: 1.35,  # پنجشنبه Thursday
    4: 1.55,  # جمعه    Friday  (busiest)
    5: 1.10,  # شنبه    Saturday
    6: 0.85,  # یکشنبه  Sunday  (quietest)
}

# Hour-of-day weights. Lunch (the main Iranian meal) outweighs dinner.
HOUR_WEIGHTS = {
    11: 2, 12: 7, 13: 10, 14: 8, 15: 4,     # lunch service
    16: 1, 17: 1, 18: 2,                     # afternoon lull
    19: 5, 20: 8, 21: 7, 22: 4, 23: 1,       # dinner service
}

# Keyword -> popularity weight for main dishes (higher = ordered more often).
MAIN_KEYWORDS = [
    (('کوبیده', 'کباب', 'جوجه', 'برگ', 'میکس', 'سلطانی'), 6.0),
    (('چلو', 'ته چین', 'باقالی', 'زرشک', 'کلم پلو'), 4.0),
    (('فسنجان', 'قورمه', 'قیمه', 'خورشت', 'کشک', 'بادمجان'), 3.5),
    (('پیتزا', 'برگر', 'سوخاری', 'فینگر', 'استیک'), 2.8),
    (('ماکارونی', 'استامبولی', 'عدس', 'پلو'), 2.5),
    (('ماهی', 'قزل'), 1.6),
]

# Names that are sides/appetizers rather than a meal on their own.
SIDE_TOKENS = ('سالاد', 'زیتون', 'ماست', 'سس', 'ترشی', 'سوپ', 'نوشیدنی')


def _weight_for_main(name):
    for tokens, w in MAIN_KEYWORDS:
        if any(t in name for t in tokens):
            return w
    return 1.5  # any other cooked dish


def _is_side(name):
    return any(t in name for t in SIDE_TOKENS)


class Command(BaseCommand):
    help = 'ایجاد داده‌های نمونه واقع‌گرایانه برای ۳ ماه گذشته (سلیقه ایرانی)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90,
                            help='تعداد روزهای گذشته برای تولید داده (پیش‌فرض ۹۰)')
        parser.add_argument('--clear', action='store_true',
                            help='حذف سفارش‌ها و موجودی قبلی پیش از تولید داده')
        parser.add_argument('--seed', type=int, default=1402,
                            help='seed تصادفی برای بازتولید‌پذیری')

    @transaction.atomic
    def handle(self, *args, **opts):
        random.seed(opts['seed'])
        days = opts['days']

        creator = self._get_creator()
        mains, sides, drinks = self._load_menu(opts['clear'])
        tables = self._ensure_tables()

        if opts['clear']:
            n_oi = OrderItem.objects.count()
            n_o = Order.objects.count()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            DailyInventory.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f'پاک‌سازی: {n_o} سفارش و {n_oi} آیتم و موجودی‌ها حذف شدند.'))

        today = timezone.localdate()
        tz = timezone.get_current_timezone()
        start = today - timedelta(days=days - 1)

        hours = list(HOUR_WEIGHTS.keys())
        hour_w = list(HOUR_WEIGHTS.values())
        main_w = [_weight_for_main(m.name) for m in mains]

        orders_to_make = []   # (created_at, status, table, customer, items[])
        seq_by_day = {}

        d = start
        while d <= today:
            mult = WEEKDAY_MULTIPLIER[d.weekday()]
            base = random.randint(14, 22)
            n_orders = max(3, int(round(base * mult)))
            if d == today:
                # Only part of today's trading has happened.
                n_orders = max(2, n_orders // 2)

            for _ in range(n_orders):
                hour = random.choices(hours, weights=hour_w, k=1)[0]
                minute = random.randint(0, 59)
                created_at = timezone.make_aware(
                    datetime(d.year, d.month, d.day, hour, minute), tz)

                status = self._pick_status(d, today)
                # 70% dine-in (assigned a table), 30% takeaway.
                table = random.choice(tables) if random.random() < 0.70 else None

                items = self._build_basket(mains, main_w, sides, drinks)
                orders_to_make.append((created_at, status, table, items))

            d += timedelta(days=1)

        self.stdout.write(f'در حال ساخت {len(orders_to_make)} سفارش ...')
        created_orders, created_items = self._persist(
            orders_to_make, creator, seq_by_day)

        self._seed_inventory(mains + drinks, today, tz)

        self.stdout.write(self.style.SUCCESS(
            f'انجام شد: {created_orders} سفارش و {created_items} آیتم سفارش '
            f'برای بازه {start} تا {today} ساخته شد.'))

    # ------------------------------------------------------------------ #
    def _get_creator(self):
        user = (User.objects.filter(is_superuser=True).first()
                or User.objects.filter(username='admin').first()
                or User.objects.first())
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.WARNING('کاربر admin ساخته شد (رمز: admin).'))
        return user

    def _load_menu(self, clearing):
        qs = MenuItem.objects.filter(is_active=True, is_available=True)
        all_items = list(qs)
        if not all_items:
            self.stderr.write('هیچ آیتم منوی فعالی یافت نشد. ابتدا منو را وارد کنید.')
            raise SystemExit(1)

        drinks = [i for i in all_items if i.category_id in (65,)]
        dough = [i for i in all_items if 'دوغ' in i.name]
        drinks = list({i.id: i for i in (drinks + dough)}.values())

        sides = [i for i in all_items
                 if i not in drinks and _is_side(i.name)]
        mains = [i for i in all_items
                 if i not in drinks and i not in sides]

        self.stdout.write(
            f'منو: {len(mains)} غذای اصلی، {len(sides)} مخلفات، {len(drinks)} نوشیدنی.')
        return mains, sides, drinks

    def _ensure_tables(self):
        if Table.objects.exists():
            return list(Table.objects.filter(is_active=True))
        specs = [
            (1, 'میز ۱', 2), (2, 'میز ۲', 2), (3, 'میز ۳', 4), (4, 'میز ۴', 4),
            (5, 'میز ۵', 4), (6, 'میز ۶', 4), (7, 'میز ۷', 6), (8, 'میز ۸', 6),
            (9, 'میز ۹', 6), (10, 'میز ۱۰', 8), (11, 'میز VIP ۱', 8),
            (12, 'میز VIP ۲', 10),
        ]
        tables = [Table.objects.create(number=n, name=nm, capacity=c)
                  for n, nm, c in specs]
        self.stdout.write(f'{len(tables)} میز ساخته شد.')
        return tables

    def _pick_status(self, day, today):
        if day == today:
            return random.choices(
                ['pending', 'preparing', 'ready', 'completed'],
                weights=[2, 3, 2, 3], k=1)[0]
        # Past days: mostly completed, a few cancelled.
        return random.choices(['completed', 'cancelled'],
                              weights=[94, 6], k=1)[0]

    def _build_basket(self, mains, main_w, sides, drinks):
        """Return a list of (menu_item, quantity) reflecting a real order."""
        basket = []
        n_main = random.choices([1, 2, 3, 4], weights=[45, 35, 15, 5], k=1)[0]
        chosen = random.choices(mains, weights=main_w, k=n_main)
        for m in chosen:
            qty = random.choices([1, 2, 3], weights=[80, 17, 3], k=1)[0]
            basket.append((m, qty))

        # Most meals come with a drink (one per ~main, capped).
        if drinks and random.random() < 0.80:
            for _ in range(random.randint(1, max(1, n_main))):
                basket.append((random.choice(drinks), 1))

        # Occasional side / appetizer.
        if sides and random.random() < 0.30:
            basket.append((random.choice(sides), 1))

        return basket

    def _persist(self, orders_to_make, creator, seq_by_day):
        order_objs = []
        for created_at, status, table, items in orders_to_make:
            day = created_at.date()
            seq_by_day[day] = seq_by_day.get(day, 0) + 1
            number = f"S-{created_at.strftime('%Y%m%d')}-{seq_by_day[day]:03d}"
            total = sum((self._unit_price(mi) * q for mi, q in items),
                        Decimal('0'))
            order_objs.append(Order(
                order_number=number,
                customer_name=random.choice(CUSTOMER_NAMES),
                customer_phone=f"09{random.randint(100000000, 399999999)}",
                total_amount=total,
                status=status,
                order_type='manual',
                created_by=creator,
                table=table,
            ))

        Order.objects.bulk_create(order_objs, batch_size=500)

        # Override auto_now_add timestamps.
        for obj, (created_at, *_rest) in zip(order_objs, orders_to_make):
            obj.created_at = created_at
        Order.objects.bulk_update(order_objs, ['created_at'], batch_size=500)

        item_objs = []
        for obj, (created_at, status, table, items) in zip(order_objs, orders_to_make):
            for mi, qty in items:
                unit = self._unit_price(mi)
                item_objs.append(OrderItem(
                    order=obj,
                    menu_item=mi,
                    quantity=qty,
                    unit_price=unit,
                    total_price=unit * qty,
                    created_at=created_at,
                ))
        OrderItem.objects.bulk_create(item_objs, batch_size=1000)
        # created_at on items also uses auto_now_add -> realign.
        OrderItem.objects.bulk_update(item_objs, ['created_at'], batch_size=1000)

        return len(order_objs), len(item_objs)

    @staticmethod
    def _unit_price(menu_item):
        if menu_item.price_with_tax:
            return menu_item.price_with_tax
        rate = Decimal('1') + (Decimal(str(menu_item.vat_rate)) / Decimal('100'))
        return menu_item.price_without_tax * rate

    def _seed_inventory(self, items, today, tz):
        """A snapshot of today's stock so restock suggestions have something
        to compare against."""
        rows = []
        for it in items:
            rows.append(DailyInventory(
                menu_item=it,
                quantity_available=random.randint(0, 30),
                date=today,
            ))
        DailyInventory.objects.bulk_create(rows, ignore_conflicts=True, batch_size=500)
        self.stdout.write(f'{len(rows)} رکورد موجودی برای امروز ساخته شد.')
