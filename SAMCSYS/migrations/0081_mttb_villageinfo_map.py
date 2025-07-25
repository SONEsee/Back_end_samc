# Generated by Django 5.0.14 on 2025-06-02 10:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0080_delete_mttb_villageinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTTB_VillageInfo_map',
            fields=[
                ('vil_id', models.AutoField(primary_key=True, serialize=False)),
                ('vil_code', models.CharField(blank=True, max_length=50, null=True)),
                ('vil_name_e', models.CharField(blank=True, max_length=50, null=True)),
                ('vil_name_l', models.CharField(blank=True, max_length=50, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('date_insert', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_update', models.DateTimeField(auto_now=True, null=True)),
                ('vbol_code', models.CharField(blank=True, max_length=50, null=True)),
                ('vbol_name', models.TextField(blank=True, null=True)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='villages', to='SAMCSYS.mttb_districtinfo')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='villages', to='SAMCSYS.mttb_provinceinfo')),
            ],
        ),
    ]
