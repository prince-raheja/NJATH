from django.conf.urls import url

from users.views import login, register, register_save, login_done, logout

app_name = 'users'


urlpatterns = [
	url(r'^register$', register, name = 'register'),
	url(r'^login$', login, name = 'login'),
	url(r'^register_done$', register_save,  name = 'register_done'),
	url(r'^login_done$', login_done, name='login_done'),
	url(r'^logout$', logout, name='logout'),
]
