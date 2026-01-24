from django.db import models

PRODUCT_STATUS = (
    ("active", "Faol"),
    ("not_active", "Faol emas"),
)

RESOLUTION_CHOICES = (
    ("1080p", "1080p"),
    ("4k", "4K"),
)


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.CharField(max_length=500)

    # 1080p uchun
    price_1080p = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    group_url_1080p = models.URLField(blank=True, null=True)

    # 4K uchun
    price_4k = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    group_url_4k = models.URLField(blank=True, null=True)

    is_active = models.CharField(max_length=50, choices=PRODUCT_STATUS, default="not_active")
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} - {self.title}"

    def get_price(self, resolution):
        return self.price_4k if resolution == "4k" else self.price_1080p

    def get_group_url(self, resolution):
        return self.group_url_4k if resolution == "4k" else self.group_url_1080p

    class Meta:
        db_table = 'products'


class Order(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    product = models.ManyToManyField(to=Product)
    count = models.IntegerField()
    resolution = models.CharField(max_length=10, choices=RESOLUTION_CHOICES, default="1080p")
    payment_method = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.pk} - {self.user}"

    class Meta:
        db_table = 'orders'