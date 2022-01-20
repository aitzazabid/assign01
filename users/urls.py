from rest_framework.routers import DefaultRouter
from users.views import SignUpView
from django.urls import path, include
from users import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter(trailing_slash=False)

router.register(r'sign_up', SignUpView)
router.register(r'getAllUser', views.GetAuthUser)
router.register(r'get_all_companies', views.ShowAllCompanies)
router.register(r'get_all_products/', views.ShowAllProducts)
router.register(r'search', views.SearchByCompanyView)
router.register(r'google_login', views.GoogleSignViewSet)
router.register(r'fuzzysearch', views.FuzzySearchView)


urlpatterns = router.urls

urlpatterns = [
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('login/', views.Login.as_view(), name='log_in'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path("getOnlyAuthUser", views.GetAuthUser.as_view({
        "get": "OnlyAuthUsers",
    })),
    path("add_profile_image/", views.UploadImages.as_view({
        "put": "set_profile_image",
    })),
    path("add_product_image/", views.UploadImages.as_view({
        "put": "set_product_image",
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
    path("delete_record", views.RecordsView.as_view({
        "delete": "destroy",
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
    path("delete_company/", views.AddCompany.as_view({
        "delete": "destroy",
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
    path("delete_product/", views.AddProducts.as_view({
        "delete": "destroy",
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
    path('resetpassword/', views.ForgotResetPassword.as_view({
        "post": "change_password"
    }), name="forgot_password"),
    path('purchase_prod/', views.PurchaseProduct.as_view({
        "post": "purchase_product"
    }), name="purchase-product"),
    path('placing_order', views.OrderView.as_view({
        "post": "create"
    }), name="placing-order"),
    path('updating_order', views.OrderView.as_view({
        "put": "update"
    }), name="updating-order"),
    path('order_status', views.OrderView.as_view({
        "get": "get_order_status"
    }), name="order-status"),
    path('contact_us/', views.ContactUsCardView.as_view({
        "post": "Send_message"
    }), name="Contact-us"),
    path('verify_account/', views.VerifyAccountView.as_view({
        "post": "send_email_or_varify"
    }), name='verify-account'),
]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
