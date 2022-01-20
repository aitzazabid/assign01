from users.models import UserProfile, Records, Company, Products, RoleModel, Orders, CompanyCatgeory, ProductCategory
from users.serializers import ProfileSerializer, UserSerializer, \
    RecordSerializer, ProductSerializer, CompanySerializer, RoleSerializer, ResetPasswordSerializer, \
    SearchProfileSerializer, OrderSerializer, ProductCategorySerializer, CompanyCategorySerializer
from rest_framework.response import Response
from django.template.loader import render_to_string
from users.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, generics
from rest_framework import filters
from rest_framework.views import APIView
from random import randint
from django.conf import settings
from django.core.mail import send_mail
from users import constants
from assign01.settings import EMAIL_HOST_USER
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.mail import EmailMultiAlternatives
from datetime import timedelta
from django.utils import timezone
from rest_fuzzysearch import search, sort


# Create your views here.


class SignUpView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data
        user_data["username"] = request.data["my_email"]
        user_data["email"] = request.data["my_email"]
        check_user = User.objects.filter(email=user_data["email"])
        if check_user:
            return Response({
                "success": False,
                'code': status.HTTP_406_NOT_ACCEPTABLE,
                "message": 'User with this email alrady exists.'}, status=status.HTTP_406_NOT_ACCEPTABLE
            )
        user = UserSerializer(data=user_data)
        if user.is_valid():
            user = user.save()
            user.set_password(request.data["password"])
            user.save()
            data = request.data
            data["user"] = user.id
            data["expires_in"] = timezone.now() + timedelta(days=7)
            data["verified"] = False
            data["my_name"] = str(data["first_name"]) + " " + str(data["last_name"])
            profile = self.get_serializer(data=data)
            if profile.is_valid():
                profile.save()
                token, created = Token.objects.get_or_create(user=user)
                response = profile.data
                response["Token"] = token.key
                return Response(response)
            return Response({
                "success": False,
                'code': status.HTTP_406_NOT_ACCEPTABLE,
                "error": profile._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        return Response({
            "success": False,
            'code': status.HTTP_406_NOT_ACCEPTABLE,
            "error": user._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
        )


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.data["email"]).first()
        if user:
            if user.profile.verified == False:
                if user.profile.expires_in > timezone.now():
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
                            'code': status.HTTP_401_UNAUTHORIZED,
                            "message": "The password that you've entered is incorrect"
                        }, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_404_NOT_FOUND,
                        "message": "Your account is banned because you did not verified your account in 7 days."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
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
                        'code': status.HTTP_401_UNAUTHORIZED,
                        "message": "The password that you've entered is incorrect"
                    }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "user does not exists"
            }, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):

    def put(self, request):
        # simply delete the token to force a login
        dt = request.data
        token = dt.get('token')
        t = Token.objects.filter(key=token).delete()
        return Response({
            'success': True,
            "message": "Logout successfull"}, status=status.HTTP_200_OK)


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
        else:
            return Response({
                "success": False,
                'code': status.HTTP_406_NOT_ACCEPTABLE,
                "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )


class UploadImages(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

    def set_profile_image(self, request):
        user_id = request.user.id
        check_user = UserProfile.objects.filter(user=user_id).first()
        if check_user:
            check_user.profile_image = request.data['image']
            check_user.save()
            return Response({
                'success': True,
                'message': 'Image saved.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'user does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)

    def set_product_image(self, request):
        user_id = request.user.id
        data = request.GET
        company_id = data.get('company_id')
        product_id = data.get('product_id')
        check_user = UserProfile.objects.filter(user=user_id)
        if check_user:
            check_company = Company.objects.filter(user=user_id).filter(id=company_id)
            if check_company:
                check_product = Products.objects.filter(id=product_id).filter(company=company_id).first()
                if check_product:
                    check_product.product_image = request.data['product_image']
                    check_product.save()
                    return Response({
                        'success': True,
                        'code': status.HTTP_200_OK
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, 'message': 'Product does not exist'},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'success': False, 'message': 'company does not exist'},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'success': False, 'message': 'user does not exist'},
                            status=status.HTTP_404_NOT_FOUND)


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
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_406_NOT_ACCEPTABLE,
                    "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                )
        return Response({
            "success": False,
            'code': status.HTTP_404_NOT_FOUND,
            "message": "User does not exist"
        }, status=status.HTTP_404_NOT_FOUND)

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
                        'code': status.HTTP_406_NOT_ACCEPTABLE,
                        "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                    )
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "User not have this product"
                }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "success": False,
            'code': status.HTTP_404_NOT_FOUND,
            "message": "User does not exist"
        }, status=status.HTTP_404_NOT_FOUND)

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
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "User's item does not exist"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        user_id = request.user.id
        check_user = UserProfile.objects.filter(user=user_id)
        if check_user:
            check_record = Records.objects.filter(id=request.GET['id']).first()
            if check_record:
                is_user_record = Records.objects.filter(user=user_id).filter(id=request.GET['id']).first()
                if is_user_record:
                    is_user_record.delete()
                    return Response({'success': True, 'message': "Product deleted."}, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_404_NOT_FOUND,
                        "message": "User has not this record."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "Record does not exist."
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "User does not exist."
            }, status=status.HTTP_404_NOT_FOUND)


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
            if request.data.get('identity'):
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
                                'code': status.HTTP_404_NOT_FOUND,
                                "message": str(i) + " User does not exist"
                            }, status=status.HTTP_404_NOT_FOUND)
                    data["user_list"] = data1
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_406_NOT_ACCEPTABLE,
                    "message": "Please enter identity."}, status=status.HTTP_406_NOT_ACCEPTABLE
                )
            data2 = {}
            if data.get('company_category') is None:
                return Response({
                    'message': 'Missed company category.',
                    'success': False
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            data2['company_category'] = data['company_category']
            invalid = {"company_category"}
            data = without_keys(data, invalid)
            serializer = CompanySerializer(data=data)
            save_company_name = UserProfile.objects.filter(user=user_id).first()
            save_company_name.company = data['company_name']
            save_company_name.save()
            if serializer.is_valid():
                serializer.save()
                data2['company'] = serializer['id'].value
                check_company_category = CompanyCategorySerializer(data=data2)
                if check_company_category.is_valid():
                    check_company_category.save()
                else:
                    Company.objects.filter(id=serializer['id'].value).delete()
                    return Response({
                        'message': 'You entered wrong company category.',
                        'success': False
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)
                data1 = {}
                data1["user"] = user_id
                data1["company"] = serializer.data['id']
                data1["identity"] = request.data["identity"]
                Roleserializer1 = RoleSerializer(data=data1)
                if Roleserializer1.is_valid():
                    Roleserializer1.save()
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_406_NOT_ACCEPTABLE,
                        "error": Roleserializer1._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                    )
                response = serializer.data
                response['Company_category'] = data2['company_category']
                return Response(response)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_406_NOT_ACCEPTABLE,
                    "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                )
        else:
            return Response({
                "success": False,
                'code': status.HTTP_401_UNAUTHORIZED,
                "message": "user cannot add company, user does not exist"
            }, status=status.HTTP_401_UNAUTHORIZED)

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
                'code': status.HTTP_404_NOT_FOUND,
                "message": "User has not any company."
            }, status=status.HTTP_404_NOT_FOUND)

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
                            if multi_user_list:
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
                            else:
                                request.data["user_list"] = request.data['ids'].split(",")
                                data1 = []
                                for i in request.data["user_list"]:
                                    if UserProfile.objects.filter(my_email=i):
                                        user1 = UserProfile.objects.filter(my_email=i).first()
                                        data1.append(user1.user.id)
                                    else:
                                        return Response({
                                            "success": False,
                                            'code': status.HTTP_404_NOT_FOUND,
                                            "message": str(i) + " User does not exist"
                                        }, status=status.HTTP_404_NOT_FOUND)
                                request.data["user_list"] = data1
                            partial = True
                            instance = self.get_object()
                            serializer = self.get_serializer(instance, data=request.data, partial=partial)
                            if serializer.is_valid():
                                self.perform_update(serializer)
                                return Response(serializer.data)
                            else:
                                return Response({
                                    "success": False,
                                    'code': status.HTTP_406_NOT_ACCEPTABLE,
                                    "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                                )
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
                                    'code': status.HTTP_406_NOT_ACCEPTABLE,
                                    "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                                )
                    else:
                        return Response({
                            "success": False,
                            'code': status.HTTP_401_UNAUTHORIZED,
                            "message": "User can not update because user is not ADMIN"
                        }, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_404_NOT_FOUND,
                        "message": "User does not exist"
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "company does not exist"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "user does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        user_id = request.user.id
        company_id = request.GET['company_id']
        check_company = RoleModel.objects.filter(user=user_id).filter(company=company_id).first()
        if check_company:
            if check_company.identity == 'ADMIN':
                Company.objects.filter(id=company_id).delete()
                CompanyCatgeory.objects.filter(company=company_id).delete()
                check_company.delete()
                return Response({
                    'success': False,
                    'message': 'Company deleted.'
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Company does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)


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
                data2 = {}
                if data.get('product_category') is None:
                    return Response({
                        'message': 'Missed product category.',
                        'success': False
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)
                data2['product_category'] = data['product_category']
                invalid = {"product_category"}

                def without_keys(d, keys):
                    return {x: d[x] for x in d if x not in keys}

                data = without_keys(request.data, invalid)
                serializer = ProductSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    data2['product'] = serializer['id'].value
                    check_category = ProductCategorySerializer(data=data2)
                    if check_category.is_valid():
                        check_category.save()
                    else:
                        Products.objects.filter(id=serializer['id'].value).delete()
                        return Response({
                            'message': 'You entered wrong product category.',
                            'success': False
                        }, status=status.HTTP_406_NOT_ACCEPTABLE)
                    response = serializer.data
                    response['Company_category'] = data2['product_category']
                    return Response(response)
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_406_NOT_ACCEPTABLE,
                        "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                    )
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "company does not exist"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_401_UNAUTHORIZED,
                "message": "Only Admin user can add product"
            }, status=status.HTTP_401_UNAUTHORIZED)

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
                            'code': status.HTTP_406_NOT_ACCEPTABLE,
                            "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                        )
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_404_NOT_FOUND,
                        "message": "user have not this product."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "company does not exist"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_401_UNAUTHORIZED,
                "message": "Only Admin user can update product"
            }, status=status.HTTP_401_UNAUTHORIZED)

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
                            'code': status.HTTP_404_NOT_FOUND,
                            "message": "Company has not any product."
                        }, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_404_NOT_FOUND,
                        "message": "Company not found."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "Company does not exist."
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                "cpde": status.HTTP_400_BAD_REQUEST,
                "message": "Enter company id."
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user_id = request.user.id
        company_id = request.GET['company_id']
        check_user_company = Company.objects.filter(user=user_id).filter(id=company_id)
        if check_user_company:
            check_product = Products.objects.filter(company=company_id).filter(id=request.GET['prod_id']).first()
            if check_product:
                ProductCategory.objects.filter(product=request.GET['prod_id']).delete()
                check_product.delete()
                return Response({'success': True, 'message': 'Product deleted.'}, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Product does not exist.'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'message': 'company does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)


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
                                'code': status.HTTP_406_NOT_ACCEPTABLE,
                                "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                            )
                    else:
                        return Response({
                            "success": False,
                            'code': status.HTTP_404_NOT_FOUND,
                            "message": "user have not this product."
                        }, status=status.HTTP_404_NOT_FOUND)
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "This user is not in list of company"
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "This company does not exist"
            }, status=status.HTTP_404_NOT_FOUND)


class ResetPassword(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_pwd")):
                return Response({"old_pwd": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_pwd"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_406_NOT_ACCEPTABLE,
                "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchByCompanyView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SearchProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['company']


class ForgotPassword(viewsets.ModelViewSet):

    def get_email(self, request, *args, **kwargs):
        if request.data.get("email", None):
            user_data = request.data
            email = user_data["email"]
            check_user = UserProfile.objects.filter(my_email=email).first()
            if check_user:
                value = randint(100000, 999999)
                ctx = {
                    'link': constants.forgot_password_link + str(value),
                    'email': email
                }
                user = UserProfile.objects.filter(my_email=email).first()
                if not user:
                    return Response({
                        "success": False,
                        'code': status.HTTP_404_NOT_FOUND,
                        "error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    subject = 'Forgot password'
                    html_content = render_to_string(template_name='forgot_password.html', context=ctx)
                    text_content = render_to_string(template_name='forgot_password.html', context=ctx)
                    msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.mixed_subtype = 'related'
                    msg.send()
                    user.forgot_password = value
                    user.save()
                    return Response({
                        'value': value,
                        'code': status.HTTP_200_OK
                    })
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "user does not exist."
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseProduct(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    def purchase_product(self, request):

        def without_keys(d, keys):
            return {x: d[x] for x in d if x not in keys}

        user_id = request.user.id
        check_user = UserProfile.objects.filter(user=user_id).first()
        if check_user:
            check_company = Company.objects.filter(id=request.GET['company_id']).filter(user=user_id)
            if check_company:
                product_id = request.GET['product_id']
                del_prod = Products.objects.filter(id=product_id).first()
                if del_prod:
                    check_prod = Products.objects.filter(id=product_id).values()[0]
                    if check_prod:
                        if check_prod['status'] == "AVAILABLE":
                            invalid = {"id"}
                            if check_user.account_balance > check_prod['price']:
                                check_user.account_balance = check_user.account_balance - check_prod['price']
                                check_user.save()
                                data = without_keys(check_prod, invalid)
                                data["company"] = request.GET['company_id']
                                data["status"] = request.data["status"]
                                serializer = ProductSerializer(data=data)
                                if serializer.is_valid():
                                    serializer.save()
                                    del_prod.delete()
                                    return Response(serializer.data)
                                else:
                                    return Response({
                                        "success": False,
                                        'code': status.HTTP_406_NOT_ACCEPTABLE,
                                        "error": serializer._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                                    )
                            else:
                                return Response({
                                    "success": False,
                                    'code': status.HTTP_406_NOT_ACCEPTABLE,
                                    "message": "user account balance is less than product price."
                                }, status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            return Response({
                                "success": False,
                                'code': status.HTTP_404_NOT_FOUND,
                                "message": "Product is not available"
                            }, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response({
                            "success": False,
                            'code': status.HTTP_404_NOT_FOUND,
                            "message": "Product is not available"
                        }, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_404_NOT_FOUND,
                        "message": "Product does not exists."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "message": "company does not exists."
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "user does not exists."
            }, status=status.HTTP_404_NOT_FOUND)


class ForgotResetPassword(viewsets.ModelViewSet):
    def change_password(self, request):
        if request.GET['pk']:
            token1 = request.GET['pk']
            user = UserProfile.objects.filter(forgot_password=token1).first()
            if user:
                user.user.set_password(request.data["new_password"])
                user.user.save()
                return Response({'success': True, 'code': status.HTTP_200_OK}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "error": "Token not found"}, status=status.HTTP_404_NOT_FOUND)


class GoogleSignViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def create(self, request, *args, **kwargs):
        if "google_id" not in request.data:
            return Response({"success": False, 'code': status.HTTP_404_NOT_FOUND, "error": {
                "google_id": [
                    "This field is required"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)
        email = request.data["google_id"]
        password = str(email) + "flicken"
        user_data = request.data
        user_data["username"] = request.data["email"]
        user_data["password"] = password
        user = UserProfile.objects.filter(google_id=request.data["google_id"]).first()
        if user:
            user = user.user
            token, created = Token.objects.get_or_create(user=user)
            response = ProfileSerializer(user.profile, context={'request': request}).data
            response["first_name"] = user.first_name
            response["last_name"] = user.last_name
            response["email"] = user.email
            response["token"] = token.key
            return Response(response)
        else:
            user = UserSerializer(data=user_data)
            if user.is_valid():
                user = user.save()
                user.set_password(password)
                user.save()

                data = request.data
                data["user"] = user.id
                data["my_name"] = str(data["first_name"]) + " " + str(data["last_name"])
                profile = self.get_serializer(data=data)
                if profile.is_valid():
                    profile.save()
                    response = profile.data
                    user.profile.check_login_attempt = 0
                    user.profile.save()
                    response["first_name"] = user.first_name
                    response["last_name"] = user.last_name
                    response["email"] = user.email
                    response["user"] = user.first_name
                    token, created = Token.objects.get_or_create(user=user)
                    response["token"] = token.key
                    response["login_attempt"] = user.profile.check_login_attempt
                    return Response(response)
                else:
                    return Response({
                        "success": False,
                        'code': status.HTTP_406_NOT_ACCEPTABLE,
                        "error": profile._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
                    )
            return Response({
                "success": False,
                'code': status.HTTP_406_NOT_ACCEPTABLE,
                "error": user._errors}, status=status.HTTP_406_NOT_ACCEPTABLE
            )


class OrderView(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        status1 = data.get('status')
        order_id1 = data.get('order_id')
        shipping_status = data.get('shipping_status')
        if shipping_status:
            return Response({
                'success': False,
                'message': 'You can not set shipping status.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if order_id1:
            return Response({
                'success': False,
                'message': 'You can not set status id.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if status1:
            return Response({
                'success': False,
                'message': 'You can not set status.'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['status'] = 'PENDING'
            product_id1 = request.GET
            prod_id = product_id1.get('prod_id')
            if prod_id:
                check_prod = Products.objects.filter(id=prod_id)
                if check_prod:
                    check_prod_status = Products.objects.filter(id=prod_id).first()
                    if check_prod_status.status == 'AVAILABLE':
                        data['product_id'] = prod_id
                        serializer = OrderSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            email = request.data["email"]
                            subject = 'Thank you for order'
                            ctx = {
                                'price': check_prod_status.price,
                                'total_price': check_prod_status.price + 200 + 50,
                                'product_price': check_prod_status.price
                            }
                            html_content = render_to_string(template_name='placing_order.html', context=ctx)
                            text_content = render_to_string(template_name='placing_order.html', context=ctx)
                            msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [email])
                            msg.attach_alternative(html_content, "text/html")
                            msg.mixed_subtype = 'related'
                            msg.send()
                            return Response({
                                'success': True,
                                'message': 'We will confirm your order shortly.'
                            }, status=status.HTTP_200_OK)
                        else:
                            return Response({
                                'success': False, 'error': serializer._errors
                            }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({
                            'success': False,
                            'message': 'Product is un avaiable.'
                        }, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({
                        'success': False,
                        'message': 'Product does not exist.'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'success': False,
                    'message': 'Enter product id.'
                }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        data = request.GET
        order_id = data.get('order_id')
        company_id = data.get('company_id')
        order = Orders.objects.filter(id=order_id).first()
        if order:
            prod_id = order.product_id
            check_prod_status = Products.objects.filter(id=prod_id.id).first()
            user_id = request.user.id
            if check_prod_status:
                if str(check_prod_status.company.id) == company_id:
                    user = RoleModel.objects.filter(user=user_id).filter(company=company_id).first()
                    if user:
                        if user.identity == 'ADMIN':
                            if check_prod_status.status == 'AVAILABLE':
                                order.shipping_status = 'ON THE WAY'
                                order.status = 'APPROVED'
                                email = order.email
                                order.save()
                                subject = 'Confirm Order'
                                ctx = {
                                    'message': 'Your order is confirm.',
                                    'order_id': order.id,
                                    'product_price': check_prod_status.price,
                                    'address': order.address,
                                    'total_price': check_prod_status.price + 200 + 50,
                                    'estimate_time': timezone.now() + timedelta(days=3),
                                    'id': order.id
                                }
                                html_content = render_to_string(template_name='confirm_order.html', context=ctx)
                                text_content = render_to_string(template_name='confirm_order.html', context=ctx)
                                msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [email])
                                msg.attach_alternative(html_content, "text/html")
                                msg.mixed_subtype = 'related'
                                msg.send()
                                return Response({
                                    'code': status.HTTP_200_OK,
                                    'message': 'Email send'
                                }, status=status.HTTP_200_OK)
                            else:
                                email = order.email
                                recipient_list = [email, ]
                                subject = 'Not Confirm product'
                                message = 'Your order cannot confirm. Product is not available.'
                                send_mail(subject, message, EMAIL_HOST_USER, recipient_list)
                                return Response({
                                    'code': status.HTTP_404_NOT_FOUND
                                }, status=status.HTTP_404_NOT_FOUND)
                        else:
                            return Response({
                                'success': False,
                                'message': 'Only Company admin user can confirm orders'
                            }, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({
                        'success': False,
                        'message': 'not match'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'success': False,
                    'message': 'Product does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'message': 'order does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    def get_order_status(self, request):
        data = request.GET
        order_id = data.get('order_id')
        if order_id:
            response = Orders.objects.filter(id=order_id).first()
            if response:
                data = OrderSerializer(response).data
                data["product_name"] = response.product_id.product_name
                return Response(data)
            else:
                return Response({
                    'message': 'order not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'message': 'order id not entered.'
            }, status=status.HTTP_404_NOT_FOUND)


class ContactUsCardView(viewsets.ModelViewSet):

    def Send_message(self, request):
        name = request.data['name']
        message = request.data['message']
        user_email = request.data['email']
        phone_number = request.data.get('phone_number')
        if phone_number:
            message1 = "Name: " + str(name) + " /n Message: " + message + " /n Sender Email: " + \
                       str(user_email) + " /n Sender Phone Number: " + str(phone_number)
        else:
            message1 = "Name: " + str(name) + " /n Message: " + message + " /n Sender Email: " + str(user_email)
        recipient_list = ['info@rfxme.com']
        if send_mail(user_email, message1, EMAIL_HOST_USER, recipient_list):
            return Response({
                "success": True,
                "message": "Mail send."
            })
        else:
            return Response({
                "success": False,
                "message": "Mail not send."
            })


class VerifyAccountView(viewsets.ModelViewSet):

    def send_email_or_varify(self, request):
        email = request.data.get('email')
        token = request.GET.get('token')
        if email:
            check_user = UserProfile.objects.filter(my_email=email).first()
            if check_user:
                value = randint(100000, 999999)
                check_user.email_verification_key = value
                check_user.save()
                ctx = {
                    'link': constants.verify_account_link + str(value),
                    'Verification_key': value
                }
                subject = 'Verify your account'
                html_content = render_to_string(template_name='send_account_verification_email.html', context=ctx)
                text_content = render_to_string(template_name='send_account_verification_email.html', context=ctx)
                msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [email])
                msg.attach_alternative(html_content, "text/html")
                msg.mixed_subtype = 'related'
                msg.send()
                return Response({
                    'message': 'verify email link send to your mail check your mail.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        elif token:
            check_user = UserProfile.objects.filter(email_verification_key=token).first()
            if check_user:
                if check_user.expires_in > timezone.now():
                    check_user.verified = True
                    check_user.save()
                    return Response({
                        'message': 'Congrats. Your account is verified.'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'message': 'You can not verify your account. The link is expired.'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "success": False,
                    'code': status.HTTP_404_NOT_FOUND,
                    "error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                "success": False,
                'code': status.HTTP_404_NOT_FOUND,
                "error": "Id or email not found"}, status=status.HTTP_404_NOT_FOUND)


class FuzzySearchView(sort.SortedModelMixin, search.SearchableModelMixin, viewsets.ReadOnlyModelViewSet):
    lookup_fields = ('company', 'country')
    lookup_value_regex = '[^/]+'
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

    filter_backends = (search.RankedFuzzySearchFilter, sort.OrderingFilter)
    search_fields = ('company', 'country')
    ordering = ('-rank',)

    min_rank = 0.1
