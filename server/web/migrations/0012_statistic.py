# Generated by Django 4.2.3 on 2023-08-17 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0011_remove_favorite_recording_requestfavorite_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('value', models.FloatField()),
            ],
        ),
    ]