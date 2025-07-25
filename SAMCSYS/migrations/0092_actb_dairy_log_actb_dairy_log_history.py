# Generated by Django 5.0.14 on 2025-06-06 03:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0091_delete_actb_dairy_log_delete_actb_dairy_log_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='ACTB_DAIRY_LOG',
            fields=[
                ('ac_entry_sr_no', models.AutoField(primary_key=True, serialize=False)),
                ('event_sr_no', models.BigIntegerField(blank=True, default=0, null=True)),
                ('event', models.CharField(blank=True, max_length=4, null=True)),
                ('drcr_ind', models.CharField(max_length=1)),
                ('fcy_amount', models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True)),
                ('exch_rate', models.DecimalField(blank=True, decimal_places=1, max_digits=24, null=True)),
                ('lcy_amount', models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True)),
                ('external_ref_no', models.CharField(blank=True, max_length=16, null=True)),
                ('addl_text', models.CharField(blank=True, max_length=255, null=True)),
                ('trn_dt', models.DateField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=1, null=True)),
                ('value_dt', models.DateField(blank=True, null=True)),
                ('Maker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Checker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Auth_Status', models.CharField(blank=True, default='U', max_length=1, null=True)),
                ('product', models.CharField(blank=True, max_length=4, null=True)),
                ('entry_seq_no', models.IntegerField(blank=True, null=True)),
                ('delete_stat', models.CharField(blank=True, max_length=1, null=True)),
                ('ac_ccy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_ccy_defn')),
                ('ac_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_glsub')),
                ('auth_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checker_DAILY_LOG', to='SAMCSYS.mttb_users')),
                ('financial_cycle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_fin_cycle')),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.sttb_modulesinfo')),
                ('period_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_per_code')),
                ('trn_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_trn_code')),
                ('trn_ref_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.detb_jrnl_log')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_glmaster')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_DAILY_LOG', to='SAMCSYS.mttb_users')),
            ],
            options={
                'verbose_name_plural': 'DAILY_LOG',
            },
        ),
        migrations.CreateModel(
            name='ACTB_DAIRY_LOG_HISTORY',
            fields=[
                ('ac_entry_sr_no', models.AutoField(primary_key=True, serialize=False)),
                ('event_sr_no', models.BigIntegerField(blank=True, default=0, null=True)),
                ('event', models.CharField(blank=True, max_length=4, null=True)),
                ('drcr_ind', models.CharField(max_length=1)),
                ('fcy_amount', models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True)),
                ('exch_rate', models.DecimalField(blank=True, decimal_places=1, max_digits=24, null=True)),
                ('lcy_amount', models.DecimalField(blank=True, decimal_places=3, max_digits=22, null=True)),
                ('external_ref_no', models.CharField(blank=True, max_length=16, null=True)),
                ('addl_text', models.CharField(blank=True, max_length=255, null=True)),
                ('trn_dt', models.DateField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=1, null=True)),
                ('value_dt', models.DateField(blank=True, null=True)),
                ('Maker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Checker_DT_Stamp', models.DateTimeField(blank=True, null=True)),
                ('Auth_Status', models.CharField(blank=True, default='U', max_length=1, null=True)),
                ('product', models.CharField(blank=True, max_length=4, null=True)),
                ('entry_seq_no', models.IntegerField(blank=True, null=True)),
                ('delete_stat', models.CharField(blank=True, max_length=1, null=True)),
                ('ac_ccy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_ccy_defn')),
                ('ac_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_glsub')),
                ('auth_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checker_DAILY_LOG_HISTORY', to='SAMCSYS.mttb_users')),
                ('financial_cycle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_fin_cycle')),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.sttb_modulesinfo')),
                ('period_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_per_code')),
                ('trn_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_trn_code')),
                ('trn_ref_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.detb_jrnl_log')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SAMCSYS.mttb_glmaster')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_DAILY_LOG_HISTORY', to='SAMCSYS.mttb_users')),
            ],
            options={
                'verbose_name_plural': 'DAILY_LOG_HISTORY',
            },
        ),
    ]
