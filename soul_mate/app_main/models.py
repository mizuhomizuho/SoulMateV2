from django.db import models

class Options(models.Model):

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, db_index=True, unique=True)
    value = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Опция'
        verbose_name_plural = 'Опции'