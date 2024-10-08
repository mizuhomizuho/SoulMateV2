# Generated by Django 5.1.1 on 2024-10-06 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_catalog', '0003_alter_elements_options_alter_elements_nick'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elements',
            name='nick',
            field=models.CharField(max_length=255),
        ),
        migrations.AddConstraint(
            model_name='elements',
            constraint=models.CheckConstraint(condition=models.Q(('nick__length__gt', 0)), name='app_catalog_elements_nick_not_empty'),
        ),
    ]
