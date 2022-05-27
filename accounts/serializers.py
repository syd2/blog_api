from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class RegisterSerializer(ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type' : 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ("id", "username", "password", "confirm_password")

    def create(self, validated_data):
        password = self.validated_data['password']
        confirm = self.validated_data['confirm_password']
        if password != confirm:
            raise serializers.ValidationError('passwords must match!')
        user = User.objects.create_user(username=validated_data.get('username'), email=None, password=validated_data.get("password"))
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('incorrect credentials')
