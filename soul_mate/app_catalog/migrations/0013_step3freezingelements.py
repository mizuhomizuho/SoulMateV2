# Generated by Django 5.1.1 on 2024-10-12 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_catalog', '0012_delete_step3freezingelements'),
    ]

    operations = [
        migrations.CreateModel(
            name='Step3FreezingElements',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('chrome', models.CharField(db_index=True, max_length=32, unique=True)),
            ],
        ),
    ]