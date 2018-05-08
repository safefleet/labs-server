from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        instance.set_password(password)
        instance.save()
        super().update(instance, validated_data)
        return instance
