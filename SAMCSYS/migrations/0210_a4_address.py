# Generated by Django 5.0.14 on 2025-07-23 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0209_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='A4_address',
            fields=[
                ('A4ID', models.IntegerField(primary_key=True, serialize=False)),
                ('BankID', models.CharField(blank=True, max_length=30, null=True)),
                ('BankCustomerID', models.CharField(blank=True, max_length=50, null=True)),
                ('BranchIDcode', models.CharField(blank=True, max_length=30, null=True)),
                ('DetailE', models.CharField(blank=True, max_length=4000, null=True)),
                ('VillageE', models.CharField(blank=True, max_length=250, null=True)),
                ('DistrictE', models.CharField(blank=True, max_length=250, null=True)),
                ('DetailL', models.CharField(blank=True, max_length=4000, null=True)),
                ('VillageL', models.CharField(blank=True, max_length=250, null=True)),
                ('DistrictL', models.CharField(blank=True, max_length=250, null=True)),
                ('ProvinceCode', models.CharField(blank=True, max_length=30, null=True)),
                ('DateInput', models.DateTimeField(blank=True, null=True)),
                ('DateUpdate', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'A4_address',
            },
        ),
    ]
