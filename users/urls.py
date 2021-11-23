from rest_framework.routers import DefaultRouter
from users.views import GetUser
from django.urls import path
from users import views

router = DefaultRouter(trailing_slash=False)

router.register(r'getUser', GetUser)

urlpatterns = router.urls

urlpatterns = [
    path("getOnlyAuthUser", views.GetAuthUser.as_view({
        "get": "OnlyAuthUser",
    })),
    path("getUsers/<str:pk>/", views.GetAuthUser.as_view({
        "put": "update",
    })),
]

urlpatterns += router.urls
