# Generated by Django 5.0.14 on 2025-07-09 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0192_alter_fa_accounting_method_ref_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fa_accounting_method',
            name='ref_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
