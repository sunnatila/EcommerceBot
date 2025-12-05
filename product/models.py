from django.db import models


PRODUCT_STATUS = (
    ("Faol", "Active"),
    ("Faol emas", "Not Active")
)

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.ImageField(upload_to='product/images/')
    group_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(choices=PRODUCT_STATUS, default="Not Active")
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} - {self.title}"


    class Meta:
        db_table = 'products'


ORDER_STATUS = (
    ("To'landi", 'Is paid'),
    ("To'lanmadi", "Is not paid")
)

class Order(models.Model):
    user_id = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    product_id = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    is_paid = models.BooleanField(choices=ORDER_STATUS, default="Is not paid")
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.user_id.fullname}"


    class Meta:
        db_table = 'orders'
