from django.urls import path
from .views import *

urlpatterns=[
    path("lsas/search/",LSASearchView.as_view(),name="lsa-search"),
]