# Generated by Django 4.2.7 on 2023-12-07 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_system_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='identity_document_number',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='identity_number',
            field=models.CharField(max_length=14, unique=True),
        ),
    ]