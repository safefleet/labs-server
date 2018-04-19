from django.db import models

# Create your models here.


class Vehicle(Model):
    type = CharField(max_length = 30)
    color = CharField(max_length = 30)


class Journey(Model):
    start_time = DateTimeField()
    end_time = DateTimeField()
    car = ForeignKey(Vehicle, on_delete=Cascade)