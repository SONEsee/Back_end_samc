# Generated by Django 5.0.14 on 2025-06-12 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0104_detb_jrnl_log_account_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='mttb_glmaster',
            name='CategoryType',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]
