# Generated by Django 5.0.14 on 2025-06-28 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0182_detb_jrnl_log_reference_sub_no_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='detb_jrnl_log',
            name='commments',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='detb_jrnl_log_hist',
            name='comments',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
