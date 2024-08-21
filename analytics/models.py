from django.db import models

# Create your models here.


class ProductData(models.Model):
    """
    Model for storing product data.
    """
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_sold = models.IntegerField()
    rating = models.FloatField()
    review_count = models.IntegerField()

    def __str__(self):
        return self.product_name + " | " + self.category + " -> " + str(self.price) + " - " + str(self.quantity_sold)