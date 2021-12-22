from django.shortcuts import render
from rest_framework import viewsets
from users.models import UserProfile, Records, Company, Products, RoleModel
from users.serializers import ProfileSerializer, UserSerializer, \
    RecordSerializer, ProductSerializer, CompanySerializer, RoleSerializer
from rest_framework.response import Response
from users.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated


# from django.core.mail import send_mail
# from django.conf import settings


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
                token, created = Token.objects.get_or_create(user=user)
                response = profile.data
                response["Token"] = token.key
                return Response(response)
            return Response({"success": False, "error": profile._errors})

        return Response({"success": False, "error": user._errors})


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.data["email"]).first()
        if user:
            if user.check_password(request.data["password"]):
                token, created = Token.objects.get_or_create(user=user)
                response = ProfileSerializer(user.profile, context={'request': request}).data
                user.profile.save()
                response["first_name"] = user.first_name
                response["last_name"] = user.last_name
                response["email"] = user.email
                response["token"] = token.key
                response["success"] = True
                return Response(response)
            else:
                return Response({
                    "success": False,
                    "message": "The password that you've entered is incorrect"
                })
        else:
            return Response({
                "success": False,
                "message": "user does not exists"
            })


class GetAuthUser(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def OnlyAuthUsers(self, request):
        users = User.objects.values()
        user = users.filter(is_superuser__in=((True,)))
        data = user
        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        return Response(serializer.data)


class RecordsView(viewsets.ModelViewSet):
    queryset = Records.objects.all()
    serializer_class = RecordSerializer

    def GetData(self, request):
        data = self.request.GET
        user_id1 = data.get('id')
        if user_id1:
            request.data['user'] = user_id1
            user_check = UserProfile.objects.filter(user_id=user_id1)
            if user_check:
                recordData = Records.objects.values()
                data = recordData
                return Response(data)
        else:
            return Response({
                "success": False,
                "message": "You need to enter user id"
            })

    def create(self, request, *args, **kwargs):
        data = self.request.GET
        user_id1 = data.get('id')
        request.data['user'] = user_id1
        user_check = UserProfile.objects.filter(user_id=user_id1)
        if user_check:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer._errors)
        return Response({
            "success": False,
            "message": "User does not exist"
        })

    def update(self, request, *args, **kwargs):
        data = self.request.GET
        user_id1 = data.get('id')
        user_check = UserProfile.objects.filter(user_id=user_id1)
        if user_check:
            partial = True
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                self.perform_update(serializer)
            return Response(serializer.data)
        return Response({
            "success": False,
            "message": "User does not exist"
        })

    def GetUserRecordsItems(self, request):
        data = self.request.GET
        user_id1 = data.get('id')
        user_check = UserProfile.objects.filter(user_id=user_id1)
        if user_check:
            user2 = Records.objects.filter(user_id=user_id1)
            if user2:
                users = Records.objects.values()
                users = users.filter(user_id=user_id1)
                data = users
                return Response(data)
            else:
                return Response({
                    "success": False,
                    "message": "User's item does not exist"
                })
        else:
            return Response({
                "success": False,
                "message": "User does not exist"
            })


class AddCompany(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = request.GET
        user = UserProfile.objects.filter(user_id=user_id['user_id'])
        if user:
            data = {}
            data["user"] = user_id['user_id']
            data["company_name"] = request.data["company_name"]
            if request.data["identity"] == "ADMIN":
                if request.data.get('ids'):
                    data["user_list"] = request.data['ids'].split(",")
                    for i in data["user_list"]:
                        if not UserProfile.objects.filter(user=i):
                            return Response({
                                "success": False,
                                "message": i + " id User does not exist"
                            })
            serializer = CompanySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                data1 = {}
                data1["user"] = user_id['user_id']
                data1["company"] = serializer.data['id']
                data1["identity"] = request.data["identity"]
                Roleserializer1 = RoleSerializer(data=data1)
                if Roleserializer1.is_valid():
                    Roleserializer1.save()
                else:
                    return Response(Roleserializer1._errors)
                return Response(serializer.data)
            else:
                return Response(serializer._errors)
        else:
            return Response({
                "success": False,
                "message": "user cannot add company, user does not exist"
            })


class AddProducts(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        id1 = request.GET
        company_id = id1["id"]
        user_id = id1["user_id"]
        is_admin_user = RoleModel.objects.filter(user=user_id).filter(company=company_id).first()
        if is_admin_user.identity == "ADMIN":
            is_company = Company.objects.filter(id=company_id)
            if is_company:
                data = request.data
                data['company'] = company_id
                serializer = ProductSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(serializer._errors)
            else:
                return Response({
                    "success": False,
                    "message": "company does not exist"
                })
        else:
            return Response({
                "success": False,
                "message": "Only Admin user can add product"
            })

    def update(self, request, *args, **kwargs):
        id1 = request.GET
        company_id = id1["company_id"]
        user_id = id1["user_id"]
        is_admin_user = RoleModel.objects.filter(user=user_id).filter(company=company_id).first()
        if is_admin_user.identity == "ADMIN":
            is_company = Company.objects.filter(id=company_id)
            if is_company:
                partial = True
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                if serializer.is_valid():
                    self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response({
                    "success": False,
                    "message": "company does not exist"
                })
        else:
            return Response({
                "success": False,
                "message": "Only Admin user can update product"
            })


class UpdateProductPultiUser(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        id1 = request.GET
        company_id = id1["company_id"]
        user_id = id1["m_user_id"]
        check_company = Company.objects.filter(id=company_id).first()
        if check_company:
            for i in check_company.user_list.all():
                if i.id == int(user_id):
                    partial = True
                    instance = self.get_object()
                    serializer = self.get_serializer(instance, data=request.data, partial=partial)
                    if serializer.is_valid():
                        self.perform_update(serializer)
                    return Response(serializer.data)
            return Response({
                "success": False,
                "message": "This user is not in list of company"
            })
        else:
            return Response({
                "success": False,
                "message": "This company does not exist"
            })
