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
            data["my_name"] = str(data["first_name"]) + " " + str(data["last_name"])
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
        instance = User.objects.filter(id=request.user.id).first()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        return Response(serializer.data)


class RecordsView(viewsets.ModelViewSet):
    queryset = Records.objects.all()
    serializer_class = RecordSerializer

    def create(self, request, *args, **kwargs):
        user_id1 = request.user.id
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
        user_id1 = request.user.id
        user_check = UserProfile.objects.filter(user_id=user_id1)
        if user_check:
            user_has_product = Records.objects.filter(user=user_id1).filter(id=kwargs['pk'])
            if user_has_product:
                partial = True
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                if serializer.is_valid():
                    self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response({
                    "success": False,
                    "message": "User not have this product"
                })
        return Response({
            "success": False,
            "message": "User does not exist"
        })

    def GetUserRecordsItems(self, request):
        user_id1 = request.user.id
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
        user_id = request.user.id
        user = UserProfile.objects.filter(user_id=user_id)
        if user:
            data = {}
            data["company_name"] = request.data["company_name"]
            invalid = {"identity"}

            def without_keys(d, keys):
                return {x: d[x] for x in d if x not in keys}

            data = without_keys(request.data, invalid)
            data["user"] = user_id
            if request.data["identity"] == "ADMIN":
                if request.data.get('ids'):
                    data["user_list"] = request.data['ids'].split(",")
                    data1 = []
                    for i in data["user_list"]:
                        if UserProfile.objects.filter(my_email=i):
                            user1 = UserProfile.objects.filter(my_email=i).first()
                            data1.append(user1.user.id)
                        else:
                            return Response({
                                "success": False,
                                "message": str(i) + " User does not exist"
                            })
                    data["user_list"] = data1
            serializer = CompanySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                data1 = {}
                data1["user"] = user_id
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

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        user = Company.objects.filter(user=user_id)
        if user:
            all_companies = Company.objects.values()
            response = all_companies.filter(user=user_id)
            data = response
            return Response(data)
        else:
            return Response({
                "success": False,
                "message": "User has not any company."
            })

    def update(self, request, *args, **kwargs):
        user_id = request.user.id
        is_user = UserProfile.objects.filter(user=user_id)
        if is_user:
            is_company = Company.objects.filter(user=user_id).filter(id=kwargs['pk']).first()
            if is_company:
                check_admin = RoleModel.objects.filter(user=user_id).filter(company=kwargs['pk']).first()
                if check_admin:
                    if check_admin.identity == 'ADMIN':
                        dict1 = {}
                        if request.data.get('ids'):
                            ids1 = []
                            multi_user_list = is_company.user_list.all()
                            dict1["user_list"] = request.data['ids'].split(",")
                            temp = 0
                            for i in dict1["user_list"]:
                                if i not in multi_user_list[temp].email:
                                    user12 = UserProfile.objects.filter(my_email=i).first()
                                    if user12:
                                        ids1.append(user12.user_id)
                                temp += 1
                            counter_list_multi_user = []
                            for i in range(len(multi_user_list)):
                                counter_list_multi_user.append(multi_user_list[i].id)
                            for i in ids1:
                                if i not in counter_list_multi_user:
                                    counter_list_multi_user.append(i)

                            request.data["user_list"] = counter_list_multi_user
                            partial = True
                            instance = self.get_object()
                            serializer = self.get_serializer(instance, data=request.data, partial=partial)
                            if serializer.is_valid():
                                self.perform_update(serializer)
                            return Response(serializer.data)
                        else:
                            partial = True
                            instance = self.get_object()
                            serializer = self.get_serializer(instance, data=request.data, partial=partial)
                            if serializer.is_valid():
                                self.perform_update(serializer)
                            return Response(serializer.data)
                    else:
                        return Response({
                            "success": False,
                            "message": "User can not update because user is not ADMIN"
                        })
                else:
                    return Response({
                        "success": False,
                        "message": "User does not exist"
                    })
            else:
                return Response({
                    "success": False,
                    "message": "company does not exist"
                })
        else:
            return Response({
                "success": False,
                "message": "user does not exist"
            })


class AddProducts(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        id1 = request.GET
        company_id = id1["id"]
        user_id = request.user.id
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
        user_id = request.user.id
        is_admin_user = RoleModel.objects.filter(user=user_id).filter(company=company_id).first()
        if is_admin_user.identity == "ADMIN":
            is_company = Company.objects.filter(id=company_id)
            if is_company:
                has_product = Products.objects.filter(company=company_id).filter(id=kwargs['pk'])
                if has_product:
                    partial = True
                    instance = self.get_object()
                    serializer = self.get_serializer(instance, data=request.data, partial=partial)
                    if serializer.is_valid():
                        self.perform_update(serializer)
                    return Response(serializer.data)
                else:
                    return Response({
                        "success": False,
                        "message": "user have not this product."
                    })
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

    def list(self, request, *args, **kwargs):
        user = request.user.id
        data = request.GET
        company_id = data["company_id"]
        if company_id:
            check_company = Company.objects.filter(id=company_id)
            if check_company:
                check_user_company = Company.objects.filter(user=user)
                if check_user_company:
                    all_products = Products.objects.values()
                    company_products = all_products.filter(company=company_id)
                    if company_products:
                        data = company_products
                        return Response(data)
                    else:
                        return Response({
                            "success": False,
                            "message": "Company has not any product."
                        })
                else:
                    return Response({
                        "success": False,
                        "message": "Company not found."
                    })
            else:
                return Response({
                    "success": False,
                    "message": "Company does not exist."
                })
        else:
            return Response({
                "success": False,
                "message": "Enter company id."
            })


class ShowAllProducts(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ['get']


class ShowAllCompanies(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    http_method_names = ['get']


class UpdateProductmultiUser(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        id1 = request.GET
        company_id = id1["company_id"]
        user_id = id1["m_user_id"]
        check_company = Company.objects.filter(id=company_id).first()
        if check_company:
            for i in check_company.user_list.all():
                if i.email == user_id:
                    has_product = Products.objects.filter(company=company_id).filter(id=kwargs['pk'])
                    if has_product:
                        partial = True
                        instance = self.get_object()
                        serializer = self.get_serializer(instance, data=request.data, partial=partial)
                        if serializer.is_valid():
                            self.perform_update(serializer)
                        return Response(serializer.data)
                    else:
                        return Response({
                            "success": False,
                            "message": "user have not this product."
                        })
            return Response({
                "success": False,
                "message": "This user is not in list of company"
            })
        else:
            return Response({
                "success": False,
                "message": "This company does not exist"
            })
