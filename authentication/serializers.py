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
        read_only_fields = ('date_created', 'date_modified')
        extra_kwargs = {
            'url': {
                'view_name': 'user-detail',
            }
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
'''
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('firstname', instance.first_name)
        instance.last_name = validated_data.get('lastname', instance.last_name)

        password = validated_data.get('password', None)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
'''


