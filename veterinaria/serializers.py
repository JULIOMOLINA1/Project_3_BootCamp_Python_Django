from datetime import date

from rest_framework import serializers

from .models import AtencionVeterinaria


class AtencionVeterinariaSerializer(serializers.ModelSerializer):
    animal_nombre = serializers.CharField(source="animal.nombre", read_only=True)

    class Meta:
        model = AtencionVeterinaria
        fields = "__all__"

    def validate_fecha_atencion(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "La fecha de atención no puede ser futura."
            )
        return value

    def validate_costo(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo.")
        return value