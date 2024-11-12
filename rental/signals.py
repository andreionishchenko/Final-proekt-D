from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group



@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        try:
            landlord_group = Group.objects.get(name='Landlord')
        except Group.DoesNotExist:
            landlord_group = Group.objects.create(name='Landlord')

        try:
            tenant_group = Group.objects.get(name='Tenant')
        except Group.DoesNotExist:
            tenant_group = Group.objects.create(name='Tenant')

        if instance.is_staff:  # Например, администраторы могут быть арендодателями
            instance.groups.add(landlord_group)
        else:
            instance.groups.add(tenant_group)

