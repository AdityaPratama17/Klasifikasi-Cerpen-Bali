# Generated by Django 4.0.2 on 2022-03-07 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceritabali', '0004_remove_document_jumlah_term'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='doc',
            field=models.TextField(),
        ),
    ]
