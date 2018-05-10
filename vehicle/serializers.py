from rest_framework import serializers
from vehicle.models import Position, Vehicle, Journey


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'number', 'type', 'color')


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'longitude', 'latitude', 'moment')


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ('id', 'start_time', 'stop_time')

