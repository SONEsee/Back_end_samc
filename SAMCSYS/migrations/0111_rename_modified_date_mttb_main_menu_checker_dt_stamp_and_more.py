# Generated by Django 5.0.14 on 2025-06-16 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0110_rename_modified_date_sttb_modulesinfo_checker_dt_stamp_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mttb_main_menu',
            old_name='modified_date',
            new_name='Checker_DT_Stamp',
        ),
        migrations.RenameField(
            model_name='mttb_main_menu',
            old_name='created_by',
            new_name='Checker_Id',
        ),
        migrations.RenameField(
            model_name='mttb_main_menu',
            old_name='created_date',
            new_name='Maker_DT_Stamp',
        ),
        migrations.RenameField(
            model_name='mttb_main_menu',
            old_name='modified_by',
            new_name='Maker_Id',
        ),
        migrations.RenameField(
            model_name='mttb_main_menu',
            old_name='is_active',
            new_name='Record_Status',
        ),
        migrations.AddField(
            model_name='mttb_main_menu',
            name='Auth_Status',
            field=models.CharField(blank=True, default='U', max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='mttb_main_menu',
            name='Once_Auth',
            field=models.CharField(blank=True, default='N', max_length=1, null=True),
        ),
    ]
