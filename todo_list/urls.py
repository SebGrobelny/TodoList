from django.conf.urls import url
from . import views

from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views

urlpatterns = [
	url(r'^$', views.home_page, name='home'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$',views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
	url(r'^list/$', views.create_list, name='create_list'),
	url(r'^list/(?P<list_id>\d+)/$', views.list_item, name='list_item'),
	url(r'^list/(?P<list_id>\d+)/(?P<todo_id>\d+)/$', views.todo_item, name='todo_item'),
]

    # url(r'^login/$', views.login, name='login'),
    # url(r'^logout/$', views.login, name='logout'),