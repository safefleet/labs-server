from django.db import models


class Position(models.Model):
    car = models.ForeignKey(Journey, on_delete=models.CASCADE())
    latitude = models.FloatField()
    longitude = models.FloatField()


class Vehicle(Model):
    type = CharField(max_length = 30)
    color = CharField(max_length = 30)


class Journey(Model):
    start_time = DateTimeField()
    end_time = DateTimeField()
    car = ForeignKey(Vehicle, on_delete=Cascade)