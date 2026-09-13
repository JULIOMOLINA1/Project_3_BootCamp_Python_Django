from django.db import models
from django.db.models import Q


class AtencionVeterinaria(models.Model):
    animal = models.ForeignKey(
        "animales.Animal",
        on_delete=models.PROTECT,
        related_name="atenciones_medicas",
        verbose_name="Animal",
        help_text="El animal puede recibir varias atenciones (historial clínico).",
    )
    fecha_atencion = models.DateField(verbose_name="Fecha de atención")
    diagnostico = models.CharField(max_length=300, verbose_name="Diagnóstico")
    tratamiento = models.TextField(verbose_name="Tratamiento")
    veterinario_responsable = models.CharField(
        max_length=150, verbose_name="Veterinario responsable"
    )
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo",
    )

    class Meta:
        verbose_name = "Atención veterinaria"
        verbose_name_plural = "Atenciones veterinarias"
        ordering = ["-fecha_atencion"]
        db_table = "atenciones_veterinarias"
        constraints = [
            models.CheckConstraint(
                check=Q(costo__gte=0),
                name="atencion_costo_gte_0",
            ),
        ]

    def __str__(self):
        return f"{self.animal.nombre} - {self.diagnostico[:50]} ({self.fecha_atencion})"