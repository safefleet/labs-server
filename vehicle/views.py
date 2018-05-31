from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from vehicle.models import Vehicle, Position, Journey
from vehicle.permissions import IsOwner
from vehicle.serializers import VehicleSerializer, PositionSerializer, JourneySerializer


class CreateListViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    A viewset that provides default `create()` and`list()` actions.
    """
    pass


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    http_method_names = ('get', 'put', 'post', 'patch', 'delete')

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=['get'], detail=True)
    def positions(self, request, pk):
        vehicle = self.get_object()
        journeys = Journey.objects.filter(vehicle=vehicle)
        positions = Position.objects.filter(journey__in=journeys)

        serializer = self.get_serializer(positions, many=True)
        return Response(serializer.data)


class JourneyViewSet(CreateListViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    http_method_names = ('get', 'post')
    permissions = (permissions.IsAuthenticated,)

    def get_queryset(self):
        vehicle = self.get_vehicle()
        return self.queryset.filter(vehicle=vehicle)

    def get_vehicle_set(self):
        return Vehicle.objects.filter(owner=self.request.user)

    def get_vehicle(self):
        return get_object_or_404(self.get_vehicle_set(), pk=self.kwargs['vehicle_id'])

    def perform_create(self, serializer):
        vehicle = self.get_vehicle()
        serializer.save(vehicle=vehicle)


class PositionViewSet(CreateListViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    http_method_names = ('get', 'post')
    permissions = (permissions.IsAuthenticated, )

    def get_queryset(self):
        journey = self.get_journey()
        return self.queryset.filter(journey=journey)

    def get_vehicle_set(self):
        return Vehicle.objects.filter(owner=self.request.user)

    def get_vehicle(self):
        return get_object_or_404(self.get_vehicle_set(), pk=self.kwargs['vehicle_id'])

    def get_journey(self):
        vehicle = self.get_vehicle()
        journeys = Journey.objects.all().filter(vehicle=vehicle)
        return get_object_or_404(journeys, pk=self.kwargs['journey_id'])

    def perform_create(self, serializer):
        journey = self.get_journey()
        serializer.save(journey=journey)
