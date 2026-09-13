from datetime import date

from rest_framework import serializers

from adopciones.models import SolicitudAdopcion
from veterinaria.models import AtencionVeterinaria
from .models import Animal, Ingreso, UbicacionTemporal


class AtencionHistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtencionVeterinaria
        fields = [
            "id",
            "fecha_atencion",
            "diagnostico",
            "tratamiento",
            "veterinario_responsable",
            "costo",
        ]


class SolicitudHistorialSerializer(serializers.ModelSerializer):
    adoptante_nombre = serializers.SerializerMethodField()
    concretada = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudAdopcion
        fields = [
            "id",
            "adoptante_id",
            "adoptante_nombre",
            "fecha_solicitud",
            "estado",
            "comentarios",
            "concretada",
        ]

    def get_adoptante_nombre(self, obj) -> str:
        return f"{obj.adoptante.nombre} {obj.adoptante.apellido}"

    def get_concretada(self, obj) -> bool:
        return hasattr(obj, "adopcion")


class IngresoSerializer(serializers.ModelSerializer):
    animal_nombre = serializers.CharField(source="animal.nombre", read_only=True)
    albergue_inicial_nombre = serializers.CharField(
        source="albergue_inicial.nombre", read_only=True
    )

    class Meta:
        model = Ingreso
        fields = "__all__"

    def validate_fecha_ingreso(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "La fecha de ingreso no puede ser futura."
            )
        return value


class UbicacionTemporalSerializer(serializers.ModelSerializer):
    animal_nombre = serializers.CharField(source="animal.nombre", read_only=True)
    albergue_nombre = serializers.CharField(source="albergue.nombre", read_only=True)

    class Meta:
        model = UbicacionTemporal
        fields = "__all__"

    def validate(self, attrs):
        fecha_entrada = attrs.get("fecha_entrada")
        fecha_salida = attrs.get("fecha_salida")
        if fecha_entrada and fecha_entrada > date.today():
            raise serializers.ValidationError(
                {"fecha_entrada": "La fecha de entrada no puede ser futura."}
            )
        if fecha_entrada and fecha_salida and fecha_salida < fecha_entrada:
            raise serializers.ValidationError(
                {"fecha_salida": "La fecha de salida no puede ser anterior a la de entrada."}
            )
        return attrs


class AnimalSerializer(serializers.ModelSerializer):
    ingresos = IngresoSerializer(many=True, read_only=True)
    ubicaciones = UbicacionTemporalSerializer(many=True, read_only=True)
    atenciones_medicas = AtencionHistorialSerializer(many=True, read_only=True)
    solicitudes = SolicitudHistorialSerializer(many=True, read_only=True)

    class Meta:
        model = Animal
        fields = "__all__"

    def validate_edad_aproximada(self, value):
        if value < 0:
            raise serializers.ValidationError("La edad no puede ser negativa.")
        if value > 50:
            raise serializers.ValidationError(
                "La edad aproximada parece irreal (máximo 50 años)."
            )
        return value