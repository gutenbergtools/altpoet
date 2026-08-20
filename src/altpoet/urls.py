"""
URL configuration for altpoet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.views.generic.base import TemplateView
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
)


from rest_framework import routers, serializers, viewsets

from altpoet.views import (
    AltViewSet,
    BookEditView,
    BookSearchView,
    DocumentViewSet,
    HomepageView,
    ImgViewSet,
    UserViewSet,
    UserSubmissionViewSet
)


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'alts', AltViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'imgs', ImgViewSet)
router.register(r'user_submissions', UserSubmissionViewSet)

urlpatterns = [
    path('', HomepageView.as_view(), name='home'),
    path('edit_book/', BookEditView.as_view(), name='edit_book'),
    path('search/', BookSearchView.as_view(), name='search'),
    path('alttext/', TemplateView.as_view(template_name='alttext.html'), name='alttext'),
    path('api/', include(router.urls)),
    
    # registration. the rest of the templates are in admin view.
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/password_reset/',
        PasswordResetView.as_view(template_name='registration/password_reset.html'),
        name='password_reset'),

    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('', include('rest_framework.urls')),
]



