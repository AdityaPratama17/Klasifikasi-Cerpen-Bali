# Generated by Django 4.0.2 on 2022-02-06 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ceritabali', '0003_document_jumlah_term'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='jumlah_term',
        ),
    ]
