from django.db import models

class Chat(models.Model):
    chat_id = models.AutoField(
        primary_key=True,
        db_column='chat_id'
    )
    user_id = models.CharField(
        max_length=32,
        db_column='user_id'
    )
    title = models.CharField(
        max_length=100,
        db_column='title'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    is_deleted = models.BooleanField(
        default=False,
        db_column='is_deleted'
    )

    class Meta:
        db_table = 'chat'
        managed = False

class Recipient(models.Model):
    chat_id = models.OneToOneField(
        Chat,
        on_delete=models.CASCADE,
        db_column='chat_id',
        primary_key=True,
        related_name='recipient'
    )
    
    gender = models.CharField(
        max_length=8,
        db_column="gender",
        null=True,
        blank=True
    )
    age_group = models.CharField(
        max_length=20,
        db_column="age_group",
        null=True,
        blank=True
    )
    relation = models.CharField(
        max_length=20,
        db_column="relation",
        null=True,
        blank=True
    )
    anniversary = models.CharField(
        max_length=50,
        db_column="anniversary",
        null=True,
        blank=True
    )
    situation_info = models.TextField(
        db_column="situation_info",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    class Meta:
        db_table = 'recipient'
        managed = False

class ChatMessage(models.Model):
    msg_id = models.AutoField(
        primary_key=True,
        db_column='msg_id'
    )
    chat_id = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        db_column='chat_id',
        related_name='messages'
    )
    sender = models.CharField(
        max_length=20,
        db_column='sender'
    )
    message = models.TextField(
        db_column='message'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at'
    )
    class Meta:
        db_table = 'chat_msg'
        managed = False