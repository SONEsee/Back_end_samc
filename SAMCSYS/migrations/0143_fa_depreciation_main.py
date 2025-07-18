# Generated by Django 5.0.14 on 2025-06-18 14:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0142_fa_asset_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='FA_Depreciation_Main',
            fields=[
                ('dm_id', models.AutoField(primary_key=True, serialize=False)),
                ('dpca_type', models.CharField(blank=True, max_length=20, null=True)),
                ('dpca_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('dpca_useful_life', models.IntegerField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('Record_Status', models.CharField(blank=True, default='C', max_length=1, null=True)),
                ('Maker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Checker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Checker_Id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checked_depreciation_main', to='SAMCSYS.mttb_users')),
                ('Maker_Id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_depreciation_main', to='SAMCSYS.mttb_users')),
                ('asset_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.fa_asset_list')),
            ],
            options={
                'verbose_name_plural': 'DepreciationMain',
            },
        ),
    ]
