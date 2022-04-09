# Generated by Django 4.0.2 on 2022-04-09 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ceritabali', '0007_document_tipe'),
    ]

    operations = [
        migrations.CreateModel(
            name='Term_prob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(max_length=255)),
                ('anak', models.FloatField()),
                ('remaja', models.FloatField()),
                ('dewasa', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='Filter',
        ),
    ]
