# Generated by Django 5.0.14 on 2025-06-07 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0095_detb_jrnl_log_ac_relative_detb_jrnl_log_fcy_cr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='detb_jrnl_log_hist',
            name='ac_relative',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='detb_jrnl_log_hist',
            name='fcy_cr',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True),
        ),
        migrations.AddField(
            model_name='detb_jrnl_log_hist',
            name='fcy_dr',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True),
        ),
        migrations.AddField(
            model_name='detb_jrnl_log_hist',
            name='lcy_cr',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True),
        ),
        migrations.AddField(
            model_name='detb_jrnl_log_hist',
            name='lcy_dr',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True),
        ),
    ]
