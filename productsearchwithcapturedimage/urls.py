"""accountantdistribution URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token
from django.conf import settings
from django.conf.urls.static import static
from django.views import generic
from django.conf.urls import url

from imagesearch.views import boundaryEdit

admin.site.site_header = "Product Platform Admin Panel"
admin.site.site_title = "Product Platform"
admin.site.index_tile = "Admin Home"

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path('manager-admin/bounding-poly-edit/<int:ref_img_id>/', boundaryEdit),
    path('manager-admin/', admin.site.urls),
    path('api/users/login/', obtain_jwt_token),
    path('api/users/', include('coreauth.urls')),
    path('api/products/', include('product.urls')),
    path('api/image-search/', include('imagesearch.urls')),
    path('api/auto-ml-search/', include('automlsearch.urls')),
]
