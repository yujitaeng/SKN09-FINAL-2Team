from django.db import models

class Chat(models.Model):
    chat_id = models.AutoField(
        primary_key=True,
        db_column='CHAT_ID'
    )
    user_id = models.CharField(
        max_length=32,
        db_column='USER_ID'
    )
    title = models.CharField(
        max_length=100,
        db_column='TITLE'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='CREATED_AT'
    )
    is_deleted = models.BooleanField(
        default=False,
        db_column='IS_DELETED'
    )

    class Meta:
        db_table = 'chat'

    def __str__(self):
        return f"Chat {self.chat_id} by User {self.user_id}"
    
class ChatMessage(models.Model):
    msg_id = models.AutoField(
        primary_key=True,
        db_column='MSG_ID'
    )
    chat_id = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        db_column='CHAT_ID'
    )
    sender = models.CharField(
        max_length=20,
        db_column='SENDER'
    )
    message = models.TextField(
        db_column='MESSAGE'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='CREATED_AT'
    )

    class Meta:
        db_table = 'chat_msg'
    
class Recipient(models.Model):
    chat_id = models.OneToOneField(
        Chat,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='CHAT_ID'
    )
    
    gender = models.CharField(
        max_length=8,
        db_column="gender"
    )
    age_group = models.CharField(
        max_length=20,
        db_column="age_group"
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
        db_column='CREATED_AT'
    )
    class Meta:
        db_table = 'recipient'
        
class Feedback(models.Model):
    msg_id = models.OneToOneField(
        ChatMessage,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='MSG_ID'
    )
    feedback = models.BooleanField(
        db_column='FEEDBACK'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='CREATED_AT'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='UPDATED_AT'
    )

    class Meta:
        db_table = 'feedback'