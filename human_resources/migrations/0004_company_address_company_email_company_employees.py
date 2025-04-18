# Generated by Django 5.0.3 on 2025-04-07 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_resources', '0003_remove_company_company_id_alter_company_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='employees',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
