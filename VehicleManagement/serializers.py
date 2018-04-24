from rest_framework import serializers
from VehicleManagement.models import Position, Vehicle, Journey


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'number', 'type', 'color')


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'car', 'longitude', 'latitude')


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'start_time', 'end_time', 'car')

