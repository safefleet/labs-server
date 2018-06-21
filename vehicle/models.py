from django.db import models
from authentication.models import User


class Vehicle(models.Model):
    id = models.IntegerField(primary_key=True)
    number = models.CharField(max_length=10)
    type = models.CharField(max_length=30)
    color = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Journey(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    @property
    def start_time(self):
        return self.position_set.first().moment

    @property
    def stop_time(self):
        return self.position_set.last().moment


class Position(models.Model):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    moment = models.DateTimeField(auto_now_add=True)

'''
from django_filters import filters

class Filter(FilterSet):
    created = DateTimeFromToRangeFilter()

    class Meta:
        model = [Journey, Position]
        fields = ['created']
'''