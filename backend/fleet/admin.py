

# Register your models here.
#fleet/admin.py
# Register your models here.
from django.contrib import admin
from .models import Car, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'daily_rate', 'twelve_hour_rate', 'status', 'category')
    list_filter = ('status', 'transmission', 'category')
    search_fields = ('brand', 'name')
    prepopulated_fields = {'slug': ('brand', 'name')} # Optional: helps autofill slug