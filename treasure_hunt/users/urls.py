from django.conf.urls import url

from users.views import login, register, register_save, login_done, logout, activate_account, forgot_password,\
						change_password, activation_pending, resend_activation_link, update_password, http_404

app_name = 'users'


urlpatterns = [
	url(r'^register$', register, name = 'register'),
	url(r'^login$', login, name = 'login'),
	url(r'^register_done$', register_save,  name = 'register_done'),
	url(r'^login_done$', login_done, name='login_done'),
	url(r'^logout$', logout, name='logout'),
	url(r'^activate$', activate_account, name='activate'),
	url(r'^forgot_password$', forgot_password, name='forgot_password'),
	url(r'^change_password$', change_password, name='change_password'),
	url(r'^update_password$',update_password, name='update_password'),
	url(r'^activation_pending$', activation_pending, name='activation_pending'),
	url(r'^resent_activation_link$', resend_activation_link, name='resend_activation_link'),
	url(r'^http_404$', http_404, name = 'http_404'),
]
