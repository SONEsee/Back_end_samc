# Generated by Django 5.0.14 on 2025-05-22 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0035_balancesheet_acc_balancesheet_mfi_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mttb_users',
            name='Maker_DT_Stamp',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
