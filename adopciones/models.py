from django.db import models


class Adoptante(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    direccion = models.CharField(max_length=250, verbose_name="Dirección")

    class Meta:
        verbose_name = "Adoptante"
        verbose_name_plural = "Adoptantes"
        ordering = ["-id"]
        db_table = "adoptantes"

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class SolicitudAdopcion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        APROBADA = "Aprobada", "Aprobada"
        RECHAZADA = "Rechazada", "Rechazada"

    animal = models.ForeignKey(
        "animales.Animal",
        on_delete=models.PROTECT,
        related_name="solicitudes",
        verbose_name="Animal",
        help_text="Un animal puede tener MÚLTIPLES solicitudes antes de ser adoptado.",
    )
    adoptante = models.ForeignKey(
        Adoptante,
        on_delete=models.PROTECT,
        related_name="solicitudes",
        verbose_name="Adoptante",
    )
    fecha_solicitud = models.DateField(verbose_name="Fecha de solicitud")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name="Estado",
    )
    comentarios = models.TextField(blank=True, verbose_name="Comentarios")

    class Meta:
        verbose_name = "Solicitud de adopción"
        verbose_name_plural = "Solicitudes de adopción"
        ordering = ["-fecha_solicitud"]
        db_table = "solicitudes_adopcion"

    def __str__(self):
        return f"{self.adoptante} -> {self.animal.nombre} ({self.estado})"


class Adopcion(models.Model):
    solicitud = models.OneToOneField(
        SolicitudAdopcion,
        on_delete=models.PROTECT,
        related_name="adopcion",
        verbose_name="Solicitud",
        help_text="Solo una adopción por solicitud Aprobada.",
    )
    fecha_adopcion = models.DateField(verbose_name="Fecha de adopción")
    seguimiento_post_adopcion = models.TextField(
        blank=True, verbose_name="Seguimiento post adopción"
    )

    class Meta:
        verbose_name = "Adopción"
        verbose_name_plural = "Adopciones"
        ordering = ["-fecha_adopcion"]
        db_table = "adopciones"

    def __str__(self):
        return f"Adopción de {self.solicitud.animal.nombre} el {self.fecha_adopcion}"


class SeguimientoAdopcion(models.Model):
    adopcion = models.ForeignKey(
        Adopcion,
        on_delete=models.PROTECT,
        related_name="seguimientos",
        verbose_name="Adopción",
    )
    fecha = models.DateField(verbose_name="Fecha")
    nota = models.TextField(verbose_name="Nota")

    class Meta:
        verbose_name = "Seguimiento de adopción"
        verbose_name_plural = "Seguimientos de adopción"
        ordering = ["-fecha"]
        db_table = "seguimientos_adopcion"

    def __str__(self):
        return f"Seguimiento {self.fecha} - {self.adopcion}"