# Generated by Django 5.1 on 2024-11-19 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_company_remove_companyquestion_company_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyquestion',
            old_name='experience',
            new_name='min_experience',
        ),
        migrations.AddField(
            model_name='companyquestion',
            name='max_experience',
            field=models.IntegerField(default=5),
        ),
    ]
