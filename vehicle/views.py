from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from vehicle.models import Vehicle, Position, Journey
from vehicle.serializers import VehicleSerializer, PositionSerializer, JourneySerializer


# list(get) and create(post) for vehicle_list
# retrieve(get), update(put), partial_update(patch) and destroy(delete) for vehicle_detail
class VehicleViewSet(viewsets.ViewSet):

    @action(methods=['get'], detail=True)
    def list(self, request):
        queryset = Vehicle.objects.all()
        serializer = VehicleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def retrieve(self, request, vehicleId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def create(self, request):
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True)
    def update(self, request, vehicleId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        serializer = VehicleSerializer(vehicle, data=request.data)
        if serializer.is_valid():
            serializer.save(vehicle = vehicle)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def partial_update(self, request, vehicleId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        serializer = VehicleSerializer(vehicle, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save(vehicle = vehicle)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def destroy(self, request, vehicleId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# list(get) for position_list
# retrieve(get) and create(post) for position_list_filter
class PositionViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=True)
    def list(self, request, vehicleId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        journeys = Journey.objects.filter(vehicle=vehicle)
        positions = Position.objects.filter(journey__in=journeys)
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def retrieve(self, request, vehicleId, journeyId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        journey = Journey.objects.get(pk=journeyId, vehicle=vehicle)
        positions = Position.objects.filter(journey=journey)
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def create(self, request,vehicleId,journeyId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        journey = Journey.objects.get(pk=journeyId, vehicle=vehicle)
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(journey=journey)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# list(get), create(post) in journey_list
class JourneyViewSet(viewsets.ViewSet):

    @action(methods=['get'], detail=True)
    def list(self, request, vehicleId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        journey = Journey.objects.filter(vehicle=vehicle)
        serializer = JourneySerializer(journey, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def create(self, request,vehicleId):
        queryset = Vehicle.objects.all()
        vehicle = get_object_or_404(queryset, pk=vehicleId)
        serializer = JourneySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vehicle= vehicle)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






#
#
# @api_view(['GET', 'POST'])
# def vehicle_list(request):
#     """
#     List all vehicles or create a new vehicle.
#     """
#     if request.method == 'GET':
#         vehicles = Vehicle.objects.all()
#         serializer = VehicleSerializer(vehicles, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         serializer = VehicleSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def vehicle_detail(request, vehicleId):
#     """
#     Retrieve, update or delete a vehicle.
#     """
#     try:
#         vehicle = Vehicle.objects.get(pk=vehicleId)
#     except Vehicle.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = VehicleSerializer(vehicle)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = VehicleSerializer(vehicle, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'PATCH':
#         serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         vehicle.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET'])
# def position_list(request, vehicleId):
#
#     try:
#         vehicle = Vehicle.objects.get(pk=vehicleId)
#
#     except Vehicle.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         journeys = Journey.objects.filter(vehicle=vehicle)
#         positions = Position.objects.filter(journey__in=journeys)
#         serializer = PositionSerializer(positions, many=True)
#         return Response(serializer.data)
#


# @api_view(['GET', 'POST'])
# def position_list_filter(request, vehicleId, journeyId):
#     try:
#         vehicle = Vehicle.objects.get(pk=vehicleId)
#         journey = Journey.objects.get(pk=journeyId, vehicle=vehicle)
#     except Journey.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#     except Vehicle.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         positions = Position.objects.filter(journey=journey)
#         serializer = PositionSerializer(positions, many=True)
#         return Response(serializer.data)
#
#     if request.method == 'POST':
#         serializer = PositionSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(journey=journey)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#
#
# @api_view(['GET', 'POST'])
# def journey_list(request, vehicleId):
#
#     try:
#         vehicle = Vehicle.objects.get(pk=vehicleId)
#     except Vehicle.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         journey = Journey.objects.filter(vehicle=vehicle)
#         serializer = JourneySerializer(journey, many=True)
#         return Response(serializer.data)
#
#     if request.method == 'POST':
#         serializer = JourneySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(vehicle=vehicle)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
