# Generated by Django 4.1.7 on 2023-03-05 16:17

from django.db import migrations, models
import rate.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_key', models.PositiveSmallIntegerField()),
                ('lat_lng_key', models.PositiveBigIntegerField()),
                ('rate', models.PositiveSmallIntegerField(validators=[rate.models.validate_rate])),
            ],
        ),
    ]
