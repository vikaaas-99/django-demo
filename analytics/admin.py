from django.contrib import admin
from .models import ProductData

# Register your models here.


@admin.register(ProductData)
class ProductDataAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
