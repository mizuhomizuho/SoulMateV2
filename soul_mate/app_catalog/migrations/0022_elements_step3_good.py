# Generated by Django 5.1.1 on 2024-10-26 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_catalog', '0021_elements_time_last_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='elements',
            name='step3_good',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
