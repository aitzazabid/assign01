from rest_framework.routers import DefaultRouter
from users.views import GetUser
from django.urls import path
from users import views

router = DefaultRouter(trailing_slash=False)

router.register(r'getUser', GetUser)
router.register(r'getAllUser', views.GetAuthUser)

urlpatterns = router.urls

urlpatterns = [
    path('login/', views.Login.as_view(), name='log_in'),
    path("getOnlyAuthUser", views.GetAuthUser.as_view({
        "get": "OnlyAuthUsers",
    })),
    path("getUsers/<str:pk>/", views.GetAuthUser.as_view({
        "put": "update",
    })),
    path("Getrecord", views.RecordsView.as_view({
        "get": "GetData",
    })),
    path("Addrecord", views.RecordsView.as_view({
        "post": "create",
    })),
    path("record/<str:pk>/", views.RecordsView.as_view({
        "put": "update",
    })),
    path("GetUserRecordsItems", views.RecordsView.as_view({
        "get": "GetUserRecordsItems",
    })),
    path("add_company/", views.AddCompany.as_view({
        "post": "create",
    })),
    path("get_company/", views.AddCompany.as_view({
        "get": "list",
    })),
    path("add_product/", views.AddProducts.as_view({
        "post": "create",
    })),
    path("get_product/", views.AddProducts.as_view({
        "get": "list",
    })),
    path("update_product/<str:pk>/", views.AddProducts.as_view({
        "put": "update",
    })),
    path("update_product_multi_user/<str:pk>/", views.UpdateProductPultiUser.as_view({
        "put": "update",
    })),
]

urlpatterns += router.urls
