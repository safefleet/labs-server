from django.db import models


class Vehicle(models.Model):
    number = models.CharField(max_length=10)
    type = models.CharField(max_length=30)
    color = models.CharField(max_length= 30)


class Journey(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    car = models.ForeignKey(Vehicle, on_delete=models.CASCADE)


class Position(models.Model):
    car = models.ForeignKey(Journey, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()