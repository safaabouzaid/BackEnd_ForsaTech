# Generated by Django 5.2.3 on 2025-07-17 02:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EvaluationResume', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resumeevaluation',
            name='improvement_tips',
        ),
    ]
