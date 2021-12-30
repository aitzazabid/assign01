from rest_framework.routers import DefaultRouter
from users.views import GetUser
from django.urls import path, include
from users import views
from django.views.generic import TemplateView

router = DefaultRouter(trailing_slash=False)

router.register(r'getUser', GetUser)
router.register(r'getAllUser', views.GetAuthUser)
router.register(r'get_all_companies', views.ShowAllCompanies)
router.register(r'get_all_products/', views.ShowAllProducts)
router.register(r'search', views.SearchByCompanyView)
router.register(r'google_login', views.GoogleSignViewSet)


urlpatterns = router.urls

urlpatterns = [

    # path('', TemplateView.as_view(template_name="index.html")),
    # path('accounts/', include('allauth.urls')),

    path('login/', views.Login.as_view(), name='log_in'),
    path("getOnlyAuthUser", views.GetAuthUser.as_view({
        "get": "OnlyAuthUsers",
    })),
    path("update_user", views.GetAuthUser.as_view({
        "put": "update",
    })),
    path("Getrecord", views.RecordsView.as_view({
        "get": "list",
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
    path("update_company/<str:pk>/", views.AddCompany.as_view({
        "put": "update",
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
    path("update_product_multi_user/<str:pk>/", views.UpdateProductmultiUser.as_view({
        "put": "update",
    })),
    path('reset-password/', views.ResetPassword.as_view(), name='reset_password'),
    path('forgot-password/', views.ForgotPassword.as_view({
        "post": "get_email"
    }), name="forgot_password"),
    path('purchase_prod/', views.PurchaseProduct.as_view({
        "post": "purchase_product"
    }), name="purchase-product")
]

urlpatterns += router.urls
