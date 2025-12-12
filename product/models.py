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


ORDER_STATUS = (
    ("is_paid", 'To\'landi'),
    ("is_not_paid", "To'lanmadi")
)

class Order(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    is_paid = models.CharField(max_length=20, choices=ORDER_STATUS, default="is_not_paid")
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.user_id.fullname}"


    class Meta:
        db_table = 'orders'
