from rest_framework import serializers

from .models import Albergue


class AlbergueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albergue
        fields = "__all__"