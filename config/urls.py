from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication APIs
    path('api/auth/', include('user_auth.urls')),

    # Career APIs
    path('api/career/', include('career.urls')),

    ]