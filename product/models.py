from django.db import models


PRODUCT_STATUS = (
    ("active", "Faol"),
    ("not_active", "Faol emas"),
)

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.CharField(max_length=500)
    group_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.CharField(max_length=50, choices=PRODUCT_STATUS, default="not_active")
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} - {self.title}"


    class Meta:
        db_table = 'products'


class Order(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    product = models.ManyToManyField(to=Product)
    count = models.IntegerField()
    payment_method = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.pk} - {self.user}"


    class Meta:
        db_table = 'orders'
