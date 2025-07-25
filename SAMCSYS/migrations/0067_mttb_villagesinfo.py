# Generated by Django 5.0.14 on 2025-06-01 16:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0066_mttb_districtsinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTTB_VillagesInfo',
            fields=[
                ('vilid', models.AutoField(db_column='VilID', primary_key=True, serialize=False)),
                ('vilcode', models.CharField(blank=True, db_collation='SQL_Latin1_General_CP1_CI_AS', db_column='VilCode', max_length=50, null=True)),
                ('vilnamee', models.CharField(blank=True, db_collation='SQL_Latin1_General_CP1_CI_AS', db_column='VilNameE', max_length=50, null=True)),
                ('vilnamel', models.CharField(blank=True, db_collation='SQL_Latin1_General_CP1_CI_AS', db_column='VilNameL', max_length=50, null=True)),
                ('userid', models.IntegerField(blank=True, db_column='UserID', null=True)),
                ('dateinsert', models.DateTimeField(blank=True, db_column='DateInsert', null=True)),
                ('dateupdate', models.DateTimeField(blank=True, db_column='DAteUpdate', null=True)),
                ('vbolcode', models.CharField(blank=True, db_collation='SQL_Latin1_General_CP1_CI_AS', db_column='VBOLCode', max_length=50, null=True)),
                ('vbolname', models.TextField(blank=True, db_collation='SQL_Latin1_General_CP1_CI_AS', db_column='VBOLName', null=True)),
                ('district', models.ForeignKey(blank=True, db_column='DisID', null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_districtsinfo')),
                ('province', models.ForeignKey(blank=True, db_column='ProID', null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_provinceinfo')),
            ],
        ),
    ]
