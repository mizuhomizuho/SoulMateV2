from django.db import models

from app_catalog.models import Elements


class Options(models.Model):

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, db_index=True, unique=True)
    value = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Опция'
        verbose_name_plural = 'Опции'

class Step2FreezingElements(models.Model):

    elements = models.OneToOneField(Elements, primary_key=True, on_delete=models.DO_NOTHING)
    process_code = models.CharField(max_length=32, db_index=True, unique=True)

class Step3FreezingElements(models.Model):

    elements = models.OneToOneField(Elements, primary_key=True, on_delete=models.DO_NOTHING)
    process_code = models.CharField(max_length=32, db_index=True, unique=True)

class Pipe(models.Model):

    id = models.AutoField(primary_key=True)
    value = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)

class Debug(models.Model):

    id = models.AutoField(primary_key=True)
    time = models.FloatField()
    value = models.TextField()