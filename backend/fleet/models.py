#fleet/models.py
# Create your models here.
from django.db import models
from django.utils.text import slugify

# 1. category 
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']  # Orders categories alphabetically

    def __str__(self):
        return self.name

# 2. the car model
class Car(models.Model):
    # dropdown options for the admin panel
    TRANSMISSION_CHOICES = [
        ('AUTO', 'Automatic'),
        ('MANUAL', 'Manual'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('RENTED', 'Rented'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    # Basic info
    name = models.CharField(max_length=201, db_index=True)
    brand = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='cars')
    slug = models.SlugField(unique=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, help_text="How many of this car do you have?")

    # --- new field for admin control --
    cleaning_time = models.PositiveIntegerField(
        default=1,
        help_text="Hours needed for cleaning between trips."
    )
    
    # specs
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    seats = models.IntegerField(default=5)
    doors = models.IntegerField(default=4)
    fuel_type = models.CharField(max_length=50, default='Petrol')

    # pricing
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="price for 24 hours")
    twelve_hour_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="price for 12 hours")

    # status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    image = models.ImageField(upload_to='cars/')
    is_featured = models.BooleanField(default=False)

    # features
    features = models.TextField(blank=True, help_text="comma separated (e.g. GPS, Bluetooth, sunroof)")
    created_at = models.DateTimeField(auto_now_add=True)

    # --- FIX FOR PAGINATION WARNING ---
    class Meta:
        ordering = ['-created_at']  # Newest cars will appear first in the API

    def save(self, *args, **kwargs):
        if not self.slug:
            # Save first to get an ID if it doesn't exist
            if not self.id:
                super().save(*args, **kwargs)
            self.slug = slugify(f"{self.brand}-{self.name}-{self.id}")
            # Save again with the new slug
            return super().save(*args, **kwargs)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.name}"