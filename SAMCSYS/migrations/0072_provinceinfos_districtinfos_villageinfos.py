# Generated by Django 5.0.14 on 2025-06-01 17:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0071_delete_mttb_provinceinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProvinceInfos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pro_code', models.CharField(blank=True, max_length=50, null=True)),
                ('pro_name_e', models.CharField(blank=True, max_length=50, null=True)),
                ('pro_name_l', models.CharField(blank=True, max_length=50, null=True)),
                ('date_insert', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_update', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DistrictInfos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dis_code', models.CharField(blank=True, max_length=50, null=True)),
                ('dis_name_e', models.CharField(blank=True, max_length=50, null=True)),
                ('dis_name_l', models.CharField(blank=True, max_length=50, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('date_insert', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_update', models.DateTimeField(auto_now=True, null=True)),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='districts', to='SAMCSYS.provinceinfos')),
            ],
        ),
        migrations.CreateModel(
            name='VillageInfos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vil_code', models.CharField(blank=True, max_length=50, null=True)),
                ('vil_name_e', models.CharField(blank=True, max_length=50, null=True)),
                ('vil_name_l', models.CharField(blank=True, max_length=50, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('date_insert', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_update', models.DateTimeField(auto_now=True, null=True)),
                ('vbol_code', models.CharField(blank=True, max_length=50, null=True)),
                ('vbol_name', models.TextField(blank=True, null=True)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='villages', to='SAMCSYS.districtinfos')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='villages', to='SAMCSYS.provinceinfos')),
            ],
        ),
    ]
