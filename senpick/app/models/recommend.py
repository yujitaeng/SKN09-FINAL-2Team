from django.db import models
from .chat import Chat
from .product import Product

class ChatRecommend(models.Model):
    rcmd_id = models.AutoField(
        primary_key=True,
        db_column='RCMD_ID'
    )
    chat_id = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        db_column='CHAT_ID'
    )
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='PRODUCT_ID'
    )
    is_liked = models.BooleanField(
        default=False,
        db_column='IS_LIKED'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='CREATED_AT'
    )
    class Meta:
        db_table = 'chat_rcmd'