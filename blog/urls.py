"""Capstone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from blog import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("",views.index, name="home"),
    path("postText",views.postText, name="postText"),
    path("profile",views.profile, name="profile"),
    path("releventPost",views.relaventPost,name="relaventPost"),
    path("logout",views.logout, name='logout'),
    path("login",views.login, name='login'),
    path("signup",views.signup, name='login'),
    path("postComment",views.postComment, name='postComment'),
    path("delete_text",views.delete_text, name='delete_post'),
    path("api",views.api_post, name='api'),
    path("new_cluster",views.new_cluster, name='new_cluster'),
    path("tofind_rel_post",views.tofind_rel_post, name='tofind_rel_post'),
    path("testing",views.testing, name='testing'),
    path("insert",views.insert, name='insert'),
    path("fetch_all",views.fetch_all, name='fetch_all'),
    path("p_all_cluster",views.p_all_cluster, name='p_all_cluster'),
    path("p_tofind_rel_post",views.p_tofind_rel_post, name='p_tofind_rel_post'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
