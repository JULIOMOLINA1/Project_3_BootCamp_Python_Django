from django.db import models


class Albergue(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    direccion = models.CharField(max_length=250, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    class Meta:
        verbose_name = "Albergue"
        verbose_name_plural = "Albergues"
        ordering = ["-id"]
        db_table = "albergues"

    def __str__(self):
        return self.nombre