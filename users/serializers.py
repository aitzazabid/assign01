from users.models import UserProfile, User, Records
from rest_framework import serializers


# from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Records
        fields = "__all__"
