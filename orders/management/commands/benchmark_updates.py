import time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import F

from orders.models import Order, UserStats


def _create_signal_style(user, count=1000):
    # Simulate the old signal approach: create orders one-by-one and update stats per-order
    start = time.perf_counter()
    stats, _ = UserStats.objects.get_or_create(user=user)
    for _ in range(count):
        order = Order.objects.create(user=user, total=Decimal('1.00'))
        # per-order update (what a signal would have done)
        stats.order_count += 1
        stats.total_spent += order.total
        stats.save()
    end = time.perf_counter()
    return end - start


def _create_optimized(user, count=1000):
    start = time.perf_counter()
    orders = [Order(user=user, total=Decimal('1.00')) for _ in range(count)]
    Order.objects.bulk_create(orders)

    # Bulk-update stats in a single query
    total_added = Decimal(count) * Decimal('1.00')
    UserStats.objects.update_or_create(
        user=user,
        defaults={
            'order_count': F('order_count') + count,
            'total_spent': F('total_spent') + total_added,
        },
    )
    end = time.perf_counter()
    return end - start


class Command(BaseCommand):
    help = 'Benchmark signal-style updates vs optimized service/bulk updates'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1000)

    def handle(self, *args, **options):
        count = options['count']
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user, _ = User.objects.get_or_create(username='benchmark_user')

        # reset stats and orders
        Order.objects.filter(user=user).delete()
        UserStats.objects.filter(user=user).delete()

        t_signal = _create_signal_style(user, count=count)

        # reset
        Order.objects.filter(user=user).delete()
        UserStats.objects.filter(user=user).delete()

        t_optimized = _create_optimized(user, count=count)

        speedup = t_signal / t_optimized if t_optimized > 0 else float('inf')

        print(f"Signal approach time: {t_signal:.6f}s")
        print(f"Optimized service time: {t_optimized:.6f}s")
        print(f"Speedup factor: {speedup:.2f}x")
