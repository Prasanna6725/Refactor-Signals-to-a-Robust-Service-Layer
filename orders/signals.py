from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, UserStats


@receiver(post_save, sender=Order)
def update_user_stats_on_order_save(sender, instance, created, **kwargs):
    """
    Legacy signal receiver that updates UserStats when an Order is created.
    This file is intentionally kept for reference; the app does not import it by default.
    """
    if created:
        user = instance.user
        stats, _ = UserStats.objects.get_or_create(user=user)
        stats.order_count += 1
        stats.total_spent += instance.total
        stats.save()
