from django.db import models

# Create your models here.
class Coupons(models.Model):
    DISCOUNT_TYPE = (
        (1, 'DE PORCENTAJE'),
        (2, 'DE CANTIDAD')
    )
    code = models.CharField(max_length=20)
    discount_type = models.PositiveSmallIntegerField(default=1)
    coupon_name = models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    use_limit = models.PositiveIntegerField(null=True)
    used_it = models.ManyToManyField('users.User', blank=True)
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code