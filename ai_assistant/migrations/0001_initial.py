from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0003_alter_usercompany_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIAssistantAccess',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
            ],
            options={
                'permissions': [
                    (
                        'can_query_factory_database',
                        'Can query factory database through AI assistant',
                    ),
                ],
                'managed': False,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='AIAssistantInteraction',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('question', models.TextField()),
                ('page', models.CharField(blank=True, default='', max_length=300)),
                ('mode', models.CharField(blank=True, default='', max_length=50)),
                ('provider', models.CharField(blank=True, default='', max_length=50)),
                ('model', models.CharField(blank=True, default='', max_length=100)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('SUCCESS', 'Success'),
                            ('ERROR', 'Error'),
                            ('BLOCKED', 'Blocked'),
                        ],
                        default='SUCCESS',
                        max_length=20,
                    ),
                ),
                ('generated_sql', models.TextField(blank=True, default='')),
                ('validation_status', models.CharField(blank=True, default='', max_length=50)),
                ('blocked_reason', models.TextField(blank=True, default='')),
                ('row_count', models.PositiveIntegerField(blank=True, null=True)),
                ('latency_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('error_code', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'company',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='ai_assistant_interactions',
                        to='company.company',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='ai_assistant_interactions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['company', 'created_at'], name='ai_assista_company_6886e8_idx'),
                    models.Index(fields=['user', 'created_at'], name='ai_assista_user_id_45f71b_idx'),
                    models.Index(fields=['mode', 'created_at'], name='ai_assista_mode_7347a0_idx'),
                    models.Index(fields=['status', 'created_at'], name='ai_assista_status_fec0c4_idx'),
                ],
            },
        ),
    ]
