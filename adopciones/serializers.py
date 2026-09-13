from datetime import date

from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers

from animales.models import Animal
from .models import Adopcion, Adoptante, SeguimientoAdopcion, SolicitudAdopcion

telefono_validator = RegexValidator(
    regex=r"^\+?[\d\s\-()]{7,20}$",
    message="Ingrese un teléfono válido (7 a 20 caracteres, solo dígitos, espacios, +, - o paréntesis).",
)


class AdoptanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adoptante
        fields = "__all__"

    def validate_telefono(self, value):
        telefono_validator(value)
        return value

    def validate_email(self, value):
        email = value.strip().lower()
        qs = Adoptante.objects.filter(email=email)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un adoptante registrado con este correo electrónico."
            )
        return email


class SolicitudAdopcionSerializer(serializers.ModelSerializer):
    animal_nombre = serializers.CharField(source="animal.nombre", read_only=True)
    adoptante_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudAdopcion
        fields = "__all__"

    def get_adoptante_nombre(self, obj) -> str:
        return f"{obj.adoptante.nombre} {obj.adoptante.apellido}"

    def validate_fecha_solicitud(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "La fecha de solicitud no puede ser futura."
            )
        return value

    def validate(self, attrs):
        animal = attrs.get("animal")
        if animal is not None and animal.estado_actual == Animal.Estado.ADOPTADO:
            raise serializers.ValidationError(
                {"animal": "Este animal ya fue adoptado, no puede recibir solicitudes."}
            )
        return attrs


class AdopcionSerializer(serializers.ModelSerializer):
    animal_id = serializers.IntegerField(source="solicitud.animal_id", read_only=True)
    animal_nombre = serializers.ReadOnlyField(source="solicitud.animal.nombre")
    adoptante_id = serializers.IntegerField(source="solicitud.adoptante_id", read_only=True)
    adoptante_nombre = serializers.SerializerMethodField()
    solicitud_estado = serializers.CharField(
        source="solicitud.estado", read_only=True
    )

    class Meta:
        model = Adopcion
        fields = "__all__"

    def get_adoptante_nombre(self, obj) -> str:
        return f"{obj.solicitud.adoptante.nombre} {obj.solicitud.adoptante.apellido}"

    def validate(self, attrs):
        solicitud = attrs.get("solicitud")
        fecha_adopcion = attrs.get("fecha_adopcion")

        if solicitud is None:
            raise serializers.ValidationError({"solicitud": "La solicitud es obligatoria."})

        if solicitud.estado != SolicitudAdopcion.Estado.APROBADA:
            raise serializers.ValidationError(
                {
                    "solicitud": (
                        "Solo puede concretarse una adopción sobre una solicitud "
                        "APROBADA."
                    )
                }
            )

        if solicitud.animal.estado_actual == Animal.Estado.ADOPTADO:
            raise serializers.ValidationError(
                {"solicitud": "Este animal ya tiene una adopción concretada."}
            )

        if fecha_adopcion and fecha_adopcion < solicitud.fecha_solicitud:
            raise serializers.ValidationError(
                {
                    "fecha_adopcion": (
                        "La fecha de adopción no puede ser anterior a la fecha "
                        "de la solicitud."
                    )
                }
            )

        qs = Adopcion.objects.filter(solicitud__animal=solicitud.animal)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"solicitud": "El animal ya fue adoptado (solo una adopción por animal)."}
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        adopcion = super().create(validated_data)
        adopcion.solicitud.animal.estado_actual = Animal.Estado.ADOPTADO
        adopcion.solicitud.animal.save(update_fields=["estado_actual"])
        return adopcion


class SeguimientoAdopcionSerializer(serializers.ModelSerializer):
    animal_id = serializers.IntegerField(
        source="adopcion.solicitud.animal_id", read_only=True
    )
    animal_nombre = serializers.ReadOnlyField(
        source="adopcion.solicitud.animal.nombre"
    )

    class Meta:
        model = SeguimientoAdopcion
        fields = "__all__"

    def validate_fecha(self, value):
        if value > date.today():
            raise serializers.ValidationError("La fecha de seguimiento no puede ser futura.")
        return value

    def validate(self, attrs):
        fecha = attrs.get("fecha")
        adopcion = attrs.get("adopcion")
        if fecha and adopcion and fecha < adopcion.fecha_adopcion:
            raise serializers.ValidationError(
                {"fecha": "El seguimiento no puede ser anterior a la fecha de adopción."}
            )
        return attrs