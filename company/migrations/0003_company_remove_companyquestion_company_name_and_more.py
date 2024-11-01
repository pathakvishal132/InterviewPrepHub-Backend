# Generated by Django 5.1 on 2024-09-17 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_companyquestion_experience_companyquestion_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='companyquestion',
            name='company_name',
        ),
        migrations.AddField(
            model_name='companyquestion',
            name='companies',
            field=models.ManyToManyField(to='company.company'),
        ),
    ]
