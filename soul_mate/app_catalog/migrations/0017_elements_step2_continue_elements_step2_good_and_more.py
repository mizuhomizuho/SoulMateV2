# Generated by Django 5.1.1 on 2024-10-15 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_catalog', '0016_elements_step1'),
    ]

    operations = [
        migrations.AddField(
            model_name='elements',
            name='step2_continue',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='elements',
            name='step2_good',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='elements',
            name='step2_parsed',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]