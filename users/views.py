from django.shortcuts import render
from rest_framework import viewsets
from users.models import UserProfile
from users.serializers import ProfileSerializer, UserSerializer
from rest_framework.response import Response
from users.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone


# Create your views here.

class GetUser(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data
        user_data["username"] = request.data["my_email"]
        user_data["email"] = request.data["my_email"]
        user = UserSerializer(data=user_data)
        if user.is_valid():
            user = user.save()
            user.set_password(request.data["password"])
            user.save()
            data = request.data
            data["user"] = user.id
            profile = self.get_serializer(data=data)
            if profile.is_valid():
                profile.save()
                response = profile.data
                return Response(response)
            return Response({"success": False, "error": profile._errors})

        return Response({"success": False, "error": user._errors})


class GetAuthUser(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def OnlyAuthUser(self, request):
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        uid_list = []
        for session in sessions:
            data = session.get_decoded()
            uid_list.append(data.get('_auth_user_id', None))
        UserData = User.objects.filter(id__in=uid_list).first()
        users = User.objects.values()
        users = users.filter(id=UserData.id).first()
        data = {}
        data = users
        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        return Response(serializer.data)
