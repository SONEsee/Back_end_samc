# Generated by Django 5.0.14 on 2025-06-16 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0106_merge_20250616_1123'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detb_jrnl_log_hist',
            old_name='Amount',
            new_name='Fcy_Amount',
        ),
        migrations.AddField(
            model_name='detb_jrnl_log_hist',
            name='Addl_sub_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='mttb_role_detail',
            unique_together={('role_id', 'sub_menu_id')},
        ),
    ]
