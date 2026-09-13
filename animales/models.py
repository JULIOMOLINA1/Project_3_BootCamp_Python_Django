from django.db import models
from django.db.models import F, Q


class Animal(models.Model):
    class Sexo(models.TextChoices):
        MACHO = "Macho", "Macho"
        HEMBRA = "Hembra", "Hembra"
        DESCONOCIDO = "Desconocido", "Desconocido"

    class Estado(models.TextChoices):
        EN_ALBERGUE = "En Albergue", "En Albergue"
        EN_ADOPCION = "En Adopción", "En Adopción"
        ADOPTADO = "Adoptado", "Adoptado"
        EN_TRATAMIENTO = "En Tratamiento", "En Tratamiento"
        FALLECIDO = "Fallecido", "Fallecido"

    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    especie = models.CharField(max_length=100, verbose_name="Especie")
    raza = models.CharField(max_length=100, blank=True, verbose_name="Raza")
    edad_aproximada = models.PositiveIntegerField(
        verbose_name="Edad aproximada (años)",
        help_text="Debe ser mayor o igual a 0.",
    )
    sexo = models.CharField(
        max_length=20,
        choices=Sexo.choices,
        default=Sexo.DESCONOCIDO,
        verbose_name="Sexo",
    )
    estado_actual = models.CharField(
        max_length=30,
        choices=Estado.choices,
        default=Estado.EN_ALBERGUE,
        verbose_name="Estado actual",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animales"
        ordering = ["-id"]
        db_table = "animales"
        constraints = [
            models.CheckConstraint(
                check=Q(edad_aproximada__gte=0),
                name="animal_edad_aproximada_gte_0",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.especie})"


class Ingreso(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name="ingresos",
        verbose_name="Animal",
        help_text="PROTECT: no permite borrar el animal si ya existe su historial.",
    )
    fecha_ingreso = models.DateField(verbose_name="Fecha de ingreso")
    motivo_ingreso = models.CharField(max_length=250, verbose_name="Motivo de ingreso")
    albergue_inicial = models.ForeignKey(
        "albergues.Albergue",
        on_delete=models.PROTECT,
        related_name="ingresos",
        verbose_name="Albergue inicial",
    )

    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ["-fecha_ingreso"]
        db_table = "ingresos"

    def __str__(self):
        return f"Ingreso de {self.animal.nombre} el {self.fecha_ingreso}"


class UbicacionTemporal(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name="ubicaciones",
        verbose_name="Animal",
    )
    albergue = models.ForeignKey(
        "albergues.Albergue",
        on_delete=models.PROTECT,
        related_name="ubicaciones",
        verbose_name="Albergue",
    )
    fecha_entrada = models.DateField(verbose_name="Fecha de entrada")
    fecha_salida = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de salida",
        help_text="Vacío = el animal permanece en este albergue.",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Ubicación temporal"
        verbose_name_plural = "Ubicaciones temporales"
        ordering = ["-fecha_entrada"]
        db_table = "ubicaciones_temporales"
        constraints = [
            models.CheckConstraint(
                check=Q(fecha_salida__gte=F("fecha_entrada")) | Q(fecha_salida__isnull=True),
                name="ubicacion_fecha_salida_no_anterior_a_entrada",
            ),
        ]

    def __str__(self):
        estado = "Activo" if self.fecha_salida is None else f"hasta {self.fecha_salida}"
        return f"{self.animal.nombre} en {self.albergue.nombre} ({estado})"