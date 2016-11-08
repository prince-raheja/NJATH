from __future__ import unicode_literals
from datetime import datetime

from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Activation(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE, null=False, blank=False)
	unique_key = models.CharField(max_length=35, null=False, blank=False, primary_key=True)
	timestamp = models.DateTimeField()

	def __str__(self):
		return self.unique_key

	def __unicode__(self):
		return self.unique_key

	def return_user(self):
		return self.user.username


class ChangePassword(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE, null=False, blank=False)
	unique_key = models.CharField(max_length=35, null=False, blank=False, primary_key=True)
	timestamp = models.DateTimeField()

	def __str__(self):
		return self.unique_key

	def __unicode__(self):
		return self.unique_key

	def return_user(self):
		return self.user.username

