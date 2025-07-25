# Generated by Django 5.0.14 on 2025-07-23 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SAMCSYS', '0213_b1_loan'),
    ]

    operations = [
        migrations.CreateModel(
            name='B1_History',
            fields=[
                ('B1ID', models.AutoField(primary_key=True, serialize=False)),
                ('BankID', models.CharField(blank=True, max_length=30, null=True)),
                ('BankCustomerID', models.CharField(blank=True, max_length=50, null=True)),
                ('BranchIDCode', models.CharField(blank=True, max_length=30, null=True)),
                ('LoanID', models.CharField(blank=True, max_length=30, null=True)),
                ('OpenDate', models.DateTimeField(blank=True, null=True)),
                ('ExpiryDate', models.DateTimeField(blank=True, null=True)),
                ('ExtensionDate', models.DateTimeField(blank=True, null=True)),
                ('InterestRate', models.FloatField(blank=True, null=True)),
                ('PurposeCode', models.CharField(blank=True, max_length=10, null=True)),
                ('AmountOfLoan', models.FloatField(blank=True, null=True)),
                ('CurrencyCode', models.CharField(blank=True, max_length=3, null=True)),
                ('OutStandingBalance', models.FloatField(blank=True, null=True)),
                ('LoanAccountNum', models.CharField(blank=True, max_length=50, null=True)),
                ('NumberOfDateSlow', models.IntegerField(blank=True, null=True)),
                ('LoanClass', models.CharField(blank=True, max_length=10, null=True)),
                ('LoanType', models.CharField(blank=True, max_length=10, null=True)),
                ('LoanTerm', models.CharField(blank=True, max_length=10, null=True)),
                ('CollaStatus', models.CharField(blank=True, max_length=1, null=True)),
                ('SconceRate', models.FloatField(blank=True, null=True)),
                ('Sconce', models.FloatField(blank=True, null=True)),
                ('RateType', models.CharField(blank=True, max_length=1, null=True)),
                ('EmpID', models.CharField(blank=True, max_length=10, null=True)),
                ('DateActive', models.CharField(blank=True, max_length=8, null=True)),
                ('LoanStatus', models.CharField(blank=True, max_length=10, null=True)),
                ('dateInsert', models.DateTimeField(blank=True, null=True)),
                ('dateUpdate', models.DateTimeField(blank=True, null=True)),
                ('ProType', models.CharField(blank=True, max_length=5, null=True)),
            ],
            options={
                'verbose_name_plural': 'B1_History',
            },
        ),
    ]
