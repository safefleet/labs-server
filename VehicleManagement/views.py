from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from VehicleManagement.models import Vehicle, Position,Journey
from VehicleManagement.serializers import VehicleSerializer, PositionSerializer , JourneySerializer


@api_view(['GET', 'POST'])
def vehicle_list(request):
    """
    List all vehicles or create a new vehicle.
    """
    if request.method == 'GET':
        vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def vehicle_detail(request, pk):
    """
    Retrieve, update or delete a vehicle.
    """
    try:
        vehicle = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = VehicleSerializer(vehicle, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def position_list(request,pk):

    try:
        vehicle = Vehicle.objects.get(pk=pk)

    except Vehicle.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        journey = Journey.objects.filter(car=vehicle)
        positions = Position.objects.filter( journey_id= journey)
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)




@api_view(['GET'])
def journey_list(request,pk):

    try:
        vehicle = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        journey = Journey.objects.filter(car=vehicle)
        serializer = JourneySerializer(journey, many=True)
        return Response(serializer.data)



@api_view(['GET'])
def position_list_filter(request, pk):
    try:
        vehicle = Vehicle.objects.get(pk=pk)
        journey = Journey.objects.get(car = vehicle)
    except Vehicle.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        positions = Position.objects.filter(journey_id=journey)
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)
