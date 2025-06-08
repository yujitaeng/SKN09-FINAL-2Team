from django.db import models

class Product(models.Model):
    product_id = models.AutoField(
        primary_key=True,
        db_column='PRODUCT_ID'
    )
    name = models.CharField(
        max_length=255,
        db_column='NAME'
    )
    image_url = models.CharField(
        max_length=255,
        db_column='IMAGE_URL',
        null=True,
        blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='PRICE'
    )
    description = models.TextField(
        db_column='DESCRIPTION',
        null=True,
        blank=True
    )
    category = models.CharField(
        max_length=50,
        db_column='CATEGORY'
    )
    product_url = models.CharField(
        max_length=255,
        db_column='PRODUCT_URL',
        null=True,
        blank=True
    )
    is_recommended = models.BooleanField(
        default=False,
        db_column='IS_RECOMMENDED'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='CREATED_AT'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='UPDATED_AT',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'product'