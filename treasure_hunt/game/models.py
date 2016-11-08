from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

QUESTION_LEVEL = (
	(1, 'Level 1'),
	(2, 'Level 2'),
	(3, 'Level 3'),
	(4, 'Level 4'),
	(5, 'Level 5'),
	(6, 'Level 6')
)

class Questions(models.Model):
	level = models.IntegerField(choices=QUESTION_LEVEL, null=False, blank=False)
	question = models.TextField(blank=False, null=False)
	answer = models.CharField(max_length=40)
	slug = models.CharField(max_length=100,unique=True,blank=False,null=False)
	penalty = models.IntegerField(null=False,blank=False)
	score = models.IntegerField(null=False, blank=False)
	# user is one who uploaded the question
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.question

	def __unicode__(self):
		return self.question

	def return_user(self):
		return self.user.username 


class QuestionImage(models.Model):
	question = models.ForeignKey(Questions, on_delete=models.CASCADE, db_index=True)
	image = models.ImageField()

	def return_question(self):
		return self.question.question


class UserAnswers(models.Model):
	question = models.ForeignKey(Questions, on_delete=models.CASCADE, db_index=True)
	user = models.ForeignKey(User,on_delete=models.CASCADE, null=True)
	correct_answer = models.BooleanField(default=False, null=False, blank=False)
	answer = models.CharField(max_length=40, null=False, blank=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.answer

	def __unicode__(self):
		return self.answer

	def return_question(self):
		return self.question.question

	def return_user(self):
		return self.user.username 


class QuestionOpened(models.Model):
	question = models.ForeignKey(Questions, on_delete=models.CASCADE)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def return_user(self):
		return self.user.username

	def return_question(self):
		return self.question.question


class UserInfo(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True, db_index=True)
	current_level = models.IntegerField(choices=QUESTION_LEVEL, null=False, blank=False, default=1)
	current_level_score = models.IntegerField(default=40, null=False, blank=False)
	current_level_opened_questions = models.IntegerField(default=0, null=False, blank=False)
	total_score = models.IntegerField(default=0, null=False, blank=False)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	disqualified = models.BooleanField(default=False,null=False, blank=False)
	bonus_question_opened = models.BooleanField(default=False, null=False, blank=False)

	def __str__(self):
		return str(self.total_score)

	def __unicode__(self):
		return str(self.total_score)

	def return_user(self):
		return self.user.username 


class UserLevelProgress(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,db_index=True)
	level = models.IntegerField(choices=QUESTION_LEVEL, null=False, blank=False, default=1)
	level_score = models.IntegerField(null=False, blank=False)
	total_question_answered = models.IntegerField(default=0, null=False, blank=False)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)

	def return_user(self):
		return self.user.username

	def __str__(self):
		return self.return_user()

	def __unicode__(self):
		return self.return_user()


