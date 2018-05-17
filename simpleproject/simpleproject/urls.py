"""simpleproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, re_path, include

from boards import views
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', views.BoardListView.as_view(), name='homepage'),
    path('acc/', include('accounts.urls')),

    path('boards/<int:board_id>/', views.TopicListView.as_view(), name='board_topics'),
    path('boards/<int:board_id>/new/', views.new_topic, name='new_topic'),
    path('new_post/', views.NewPostView.as_view(), name='new_post'),

    path('boards/<int:board_id>/topics/<int:topic_id>',
         views.PostListView.as_view(), name='topic_posts'),
    path('boards/<int:board_id>/topics/<int:topic_id>/reply/',
         views.reply_topic, name='reply_topic'),
    path('boards/<int:board_id>/topics/<int:topic_id>/posts/<int:post_id>/edit',
         views.PostUpdateView.as_view(), name='edit_post'),
    path('boards/<int:board_id>/topics/<int:topic_id>/posts/<int:post_id>/delete',
         views.delete_post, name='del_post'),
]
