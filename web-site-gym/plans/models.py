from django.db import models
from django.utils import timezone
from users.models import User

# Create your models here.


class Plan(models.Model):
    class KindPlan(models.TextChoices):
        MONTHLY = 'mensal', 'Trimestal'
        QUARTERLY = 'trimestal', 'Trimestral'
        ANNUAL = 'anual', 'Anual'

    class Status(models.TextChoices):
        ACTIVE = 'ativo', 'Ativo'
        PENDING = 'pendente', 'Pendente'
        CANCELLED = 'cancelado', 'Cancelado'

    kind_plan = models.CharField(max_length=15, choices=KindPlan.choices, null=False, default='pendente')
    is_valid = models.BooleanField(default=True, verbose_name='Valido')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    create_at = models.DateField(auto_now_add=True)
    expected_payment = models.DateField(blank=True, null=True, default=timezone.localdate)
    payment_id = models.CharField(max_length=20, unique=True, null=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='plan'
    )

    def __str__(self):
        return f'Payment ID: {self.id} - Is valid: {self.is_valid} - Is active: {self.is_active}'
