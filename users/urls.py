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
]

urlpatterns += router.urls
