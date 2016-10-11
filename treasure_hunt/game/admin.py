from django.contrib import admin
from django.contrib.auth.models import User
from game.models import Questions, UserAnswers, UserInfo, UserLevelProgress, \
 						QuestionImage, QuestionOpened
# Register your models here.


class QuestionsModelAdmin(admin.ModelAdmin):
	list_display = ['level','question','answer']
	class Meta:
		model = Questions

admin.site.register(Questions, QuestionsModelAdmin)


class UserAnswersModelAdmin(admin.ModelAdmin):
	list_display = ['return_question','return_user','answer','correct_answer','timestamp']
	class Meta:
		model = UserAnswers

admin.site.register(UserAnswers, UserAnswersModelAdmin)


class UserInfoModelAdmin(admin.ModelAdmin):
	list_display = ['return_user','current_level','total_score','updated']
	class Meta:
		model = UserInfo

admin.site.register(UserInfo, UserInfoModelAdmin)


class UserLevelProgressModelAdmin(admin.ModelAdmin):
	list_display = ['return_user', 'level', 'level_score']
	class Meta:
		model = UserLevelProgress

admin.site.register(UserLevelProgress, UserLevelProgressModelAdmin)


class QuestionImageModelAdmin(admin.ModelAdmin):
	list_display = ['return_question', 'image']
	class Meta:
		model = QuestionImage

admin.site.register(QuestionImage, QuestionImageModelAdmin)



class QuestionOpenedModelAdmin(admin.ModelAdmin):
	list_display = ['return_user','return_question', 'timestamp']
	class Meta:
		model = QuestionOpened

admin.site.register(QuestionOpened, QuestionOpenedModelAdmin)