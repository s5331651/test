# Generated by Django 5.0.6 on 2024-06-04 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arduino_id', models.CharField(max_length=100, unique=True)),
                ('sim_id', models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]