from decimal import Decimal
from django.test import TestCase

from django.contrib.auth import get_user_model
from orders import services
from orders.models import Order, UserStats


User = get_user_model()


class ServiceTests(TestCase):
    def test_create_order_updates_stats(self):
        u = User.objects.create_user('svc')
        order = services.create_order(u, Decimal('12.34'))
        self.assertIsInstance(order, Order)
        stats = UserStats.objects.get(user=u)
        self.assertEqual(stats.order_count, 1)
        self.assertEqual(stats.total_spent, Decimal('12.34'))

    def test_order_create_does_not_trigger_stats_by_default(self):
        # Since signals are not registered at app startup, creating an order
        # directly should NOT update UserStats automatically.
        u = User.objects.create_user('direct')
        Order.objects.create(user=u, total=Decimal('3.00'))
        exists = UserStats.objects.filter(user=u).exists()
        self.assertFalse(exists)
