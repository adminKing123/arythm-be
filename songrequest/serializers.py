from rest_framework import serializers
from .models import SongRequest

class SongRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongRequest
        fields = "__all__"
        read_only_fields = ["user"]  # User will be set automatically from request
