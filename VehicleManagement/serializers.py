class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'number', 'type', 'color')
from rest_framework import serializers
from VehicleManagement.models import Position,Vehicle,Journey

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('car', 'longitude', 'latitude')

class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('start_time', 'end_time', 'car')



