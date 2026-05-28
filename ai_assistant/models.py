from django.conf import settings
from django.db import models


class AIAssistantAccess(models.Model):
    """Permission carrier for assistant capabilities."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ('can_query_factory_database', 'Can query factory database through AI assistant'),
        ]


class AIAssistantInteraction(models.Model):
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_ERROR = 'ERROR'
    STATUS_BLOCKED = 'BLOCKED'

    STATUS_CHOICES = (
        (STATUS_SUCCESS, 'Success'),
        (STATUS_ERROR, 'Error'),
        (STATUS_BLOCKED, 'Blocked'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_assistant_interactions',
    )
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_assistant_interactions',
    )
    question = models.TextField()
    page = models.CharField(max_length=300, blank=True, default='')
    mode = models.CharField(max_length=50, blank=True, default='')
    provider = models.CharField(max_length=50, blank=True, default='')
    model = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS)
    generated_sql = models.TextField(blank=True, default='')
    validation_status = models.CharField(max_length=50, blank=True, default='')
    blocked_reason = models.TextField(blank=True, default='')
    row_count = models.PositiveIntegerField(null=True, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    error_code = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'created_at'], name='ai_assista_company_6886e8_idx'),
            models.Index(fields=['user', 'created_at'], name='ai_assista_user_id_45f71b_idx'),
            models.Index(fields=['mode', 'created_at'], name='ai_assista_mode_7347a0_idx'),
            models.Index(fields=['status', 'created_at'], name='ai_assista_status_fec0c4_idx'),
        ]

    def __str__(self):
        return f'{self.company_id or "-"} {self.mode or "-"} {self.status}'
