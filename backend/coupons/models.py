#backend/coupons/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
# Create your models here.

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="e.g., SUMMER20")
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percentage value (1 to 100)"
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= self.valid_to
