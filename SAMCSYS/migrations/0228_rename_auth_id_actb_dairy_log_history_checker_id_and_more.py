# Generated by Django 5.0.14 on 2025-07-25 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0227_rename_auth_id_actb_dairy_log_checker_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actb_dairy_log_history',
            old_name='auth_id',
            new_name='Checker_id',
        ),
        migrations.RenameField(
            model_name='actb_dairy_log_history',
            old_name='user_id',
            new_name='Maker_id',
        ),
        migrations.AlterField(
            model_name='actb_dairy_log_history',
            name='trn_ref_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='actb_dairy_log_history',
            name='trn_ref_sub_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
