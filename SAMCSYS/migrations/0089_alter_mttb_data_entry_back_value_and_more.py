# Generated by Django 5.0.14 on 2025-06-05 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0088_alter_mttb_glmaster_res_ccy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mttb_data_entry',
            name='BACK_VALUE',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='mttb_data_entry',
            name='MOD_NO',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]
