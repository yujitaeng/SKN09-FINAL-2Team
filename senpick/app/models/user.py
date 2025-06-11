import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# Create your models here.
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수 입력 항목입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, nickname, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(primary_key=True, max_length=32, editable=False, db_column='USER_ID')
    email = models.EmailField(max_length=255, unique=True, db_column='EMAIL')
    password = models.CharField(max_length=255, db_column='PASSWORD')
    nickname = models.CharField(max_length=30, db_column='NICKNAME')
    birth = models.CharField(max_length=8, db_column='BIRTH')
    gender = models.CharField(max_length=8, db_column='GENDER')
    job = models.CharField(max_length=50, null=True, blank=True, db_column='JOB')
    profile_image = models.CharField(max_length=255, null=True, blank=True, db_column='PROFILE_IMAGE')
    type = models.CharField(max_length=10, default='guest', db_column='TYPE')
    social_provider = models.CharField(max_length=10, null=True, blank=True, db_column='SOCIAL_PROVIDER')
    is_email_verified = models.BooleanField(default=False, db_column='IS_EMAIL_VERIFIED')

    # Django 인증/권한 시스템 필수 필드
    is_active = models.BooleanField(default=True, db_column='IS_ACTIVE')
    is_staff = models.BooleanField(default=False, db_column='IS_STAFF')
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now, db_column='DATE_JOINED')
    reason = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='REASON'
    )

    # MySQL이 INSERT 시 CURRENT_TIMESTAMP를 넣도록 두고,
    # Django는 값을 지정하지 않음.
    created_at = models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')
    # INSERT 당시엔 NULL, 이후 UPDATE 시 MySQL이 자동으로 채워 주도록 둠.
    updated_at = models.DateTimeField(null=True, blank=True, db_column='UPDATED_AT')
    is_deleted = models.BooleanField(
        default=False,
        db_column='IS_DELETED'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    @property
    def pk(self):
        return self.user_id

    @property
    def id(self):
        return self.user_id
    
    class Meta:
        db_table = 'user'

    def save(self, *args, **kwargs):
        # user_id(UUID) 가 없으면, 하이픈 없는 32자리 hex 문자열 생성
        if not self.user_id:
            self.user_id = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or str(self.user_id)

class PreferType(models.Model):
    prefer_id = models.AutoField(
        primary_key=True,
        db_column='PREFER_ID'
    )
    type = models.CharField(
        max_length=20,
        db_column='TYPE'
    )
    type_name = models.CharField(
        max_length=100,
        db_column='TYPE_NAME'
    )

    class Meta:
        db_table = 'prefer_type'

    def __str__(self):
        return f"{self.type} / {self.type_name}"

class UserPrefer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='USER_ID',
        related_name='preferences'
    )
    prefer_type = models.ForeignKey(
        PreferType,
        on_delete=models.CASCADE,
        db_column='PREFER_ID',
        related_name='user_preferences'
    )
    created_at  = models.DateTimeField(
        auto_now_add=True,
        db_column='CREATED_AT'
    )
    # UPDATE 시에만 MySQL의 ON UPDATE CURRENT_TIMESTAMP가 동작하게 두려면 auto_now 제거
    updated_at  = models.DateTimeField(
        null=True,
        blank=True,
        db_column='UPDATED_AT'
    )

    class Meta:
        db_table = 'user_prefer'
        unique_together = (('user', 'prefer_type'),)

    def __str__(self):
        return f"{self.user.email} → {self.prefer_type.type_name}"
