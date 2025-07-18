# Generated by Django 5.0.14 on 2025-06-21 07:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0160_merge_20250621_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mttb_eoc_maintain',
            name='function_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_function_desc'),
        ),
        migrations.AlterField(
            model_name='mttb_eoc_maintain',
            name='module_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.sttb_modulesinfo'),
        ),
        migrations.AlterField(
            model_name='sttb_eoc_status',
            name='function_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_function_desc'),
        ),
        migrations.AlterField(
            model_name='sttb_eoc_status',
            name='module_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.sttb_modulesinfo'),
        ),
    ]
