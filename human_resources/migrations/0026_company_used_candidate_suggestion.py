# Generated by Django 5.2.3 on 2025-07-14 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('human_resources', '0025_alter_companyad_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='used_candidate_suggestion',
            field=models.BooleanField(default=False),
        ),
    ]
