from decimal import Decimal
from django.test import TestCase
from django.db.models.signals import post_save

from django.contrib.auth import get_user_model
from orders.models import Order, UserStats


User = get_user_model()


def receiver_update_stats(sender, instance, created, **kwargs):
    if created:
        stats, _ = UserStats.objects.get_or_create(user=instance.user)
        stats.order_count += 1
        stats.total_spent += instance.total
        stats.save()


class SignalTests(TestCase):
    def setUp(self):
        post_save.connect(receiver_update_stats, sender=Order)

    def tearDown(self):
        post_save.disconnect(receiver_update_stats, sender=Order)

    def test_bulk_update_bypasses_signal(self):
        # Create two users
        u1 = User.objects.create_user('u1')
        u2 = User.objects.create_user('u2')

        # Create some initial orders for u1
        Order.objects.create(user=u1, total=Decimal('10.00'))
        Order.objects.create(user=u1, total=Decimal('5.00'))

        stats = UserStats.objects.get(user=u1)
        self.assertEqual(stats.order_count, 2)
        self.assertEqual(stats.total_spent, Decimal('15.00'))

        # Create bulk orders for u2
        bulk = [Order(user=u2, total=Decimal('1.00')) for _ in range(3)]
        Order.objects.bulk_create(bulk)

        # Now change ownership of those orders to u1 via QuerySet.update()
        Order.objects.filter(user=u2).update(user=u1)

        # Signals should NOT have fired for the update()
        stats.refresh_from_db()
        self.assertEqual(stats.order_count, 2)
        self.assertEqual(stats.total_spent, Decimal('15.00'))

    def test_signal_isolation_disconnects(self):
        u = User.objects.create_user('iso')
        Order.objects.create(user=u, total=Decimal('2.00'))
        stats = UserStats.objects.get(user=u)
        self.assertEqual(stats.order_count, 1)
