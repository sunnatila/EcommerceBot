from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_remove_product_group_url_remove_product_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]
