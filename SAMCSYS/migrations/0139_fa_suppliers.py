# Generated by Django 5.0.14 on 2025-06-18 09:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0138_fa_chart_of_asset'),
    ]

    operations = [
        migrations.CreateModel(
            name='FA_Suppliers',
            fields=[
                ('supplier_id', models.AutoField(primary_key=True, serialize=False)),
                ('supplier_code', models.CharField(blank=True, max_length=20, null=True)),
                ('supplier_name', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_person', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('tax_id', models.CharField(blank=True, max_length=20, null=True)),
                ('bank_account', models.CharField(blank=True, max_length=50, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=100, null=True)),
                ('supplier_type', models.CharField(blank=True, max_length=50, null=True)),
                ('credit_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('payment_terms', models.CharField(blank=True, max_length=100, null=True)),
                ('Record_Status', models.CharField(blank=True, default='C', max_length=1, null=True)),
                ('Maker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Checker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Checker_Id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checked_asset_suppliers', to='SAMCSYS.mttb_users')),
                ('Maker_Id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_asset_suppliers', to='SAMCSYS.mttb_users')),
            ],
            options={
                'verbose_name_plural': 'AssetSuppliers',
            },
        ),
    ]
