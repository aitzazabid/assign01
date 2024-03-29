from users.models import UserProfile, User, Records, Company, Products, RoleModel, Orders, ProductCategory, \
    CompanyCatgeory
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


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class CompanyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyCatgeory
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleModel
        fields = "__all__"


class ResetPasswordSerializer(serializers.Serializer):
    model = User
    old_pwd = serializers.CharField(required=True)
    new_pwd = serializers.CharField(required=True)


class SearchProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        extra_kwargs = {'user': {'write_only': True}}


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = "__all__"
