from django.contrib import admin

# Register your models here.
from users.models import Activation, ChangePassword

class ActivationModelAdmin(admin.ModelAdmin):
	list_display = ['return_user','unique_key','timestamp']
	class Meta:
		model = Activation

admin.site.register(Activation, ActivationModelAdmin)


class ChangePasswordModelAdmin(admin.ModelAdmin):
	list_display = ['return_user','unique_key','timestamp']
	class Meta:
		model = ChangePassword

admin.site.register(ChangePassword, ChangePasswordModelAdmin)