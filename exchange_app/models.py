from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Ad(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('books', 'Книги'),
        ('clothing', 'Одежда'),
        ('other', 'Другое'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/У'),
        ('broken', 'Неисправный'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='sent_proposals'
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='received_proposals'
    )
    comment = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Предложение {self.id}: {self.ad_sender} -> {self.ad_receiver}"

    def clean(self):
        if self.ad_sender == self.ad_receiver:
            raise ValidationError("Нельзя создавать предложение на обмен с самим собой")
        
        if self.ad_sender.user == self.ad_receiver.user:
            raise ValidationError("Нельзя создавать предложение между своими объявлениями")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
