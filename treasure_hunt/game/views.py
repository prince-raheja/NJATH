from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count

# third party django app imports
from django_ajax.decorators import ajax


from game.models import Questions, UserAnswers, UserInfo, UserLevelProgress,\
						 QuestionImage, QuestionOpened


minimum_question_answered = 6
minumum_level_points = 40
max_levels = 6



# to add
# add penalty of opening bonus question and not answering
def next_level(request):
	if request.user.is_authenticated():
		username = request.user
		user = User.objects.get(username=username)
		user_info = UserInfo.objects.get(user=user)
		question_answered = user_info.current_level_answered_questions
		opened_questions = user_info.current_level_opened_questions
		if question_answered < minimum_question_answered:
			messages.success(request, 'Answer at least 6 questions in Current Level First to proceed')
			return HttpResponseRedirect(reverse('game:profile'))
		try:
			user_level_score = UserLevelProgress.objects.get(user=user, level=user_info.current_level)
			return HttpResponse('Already Played that level')
		except UserLevelProgress.DoesNotExist:
			user_level_score = UserLevelProgress.objects.create(user=user, level=user_info.current_level, \
				level_score=user_info.current_level_score,total_question_answered=question_answered,\
				total_opened_questions=opened_questions)
			user_info.current_level += 1
			if user_info.current_level > 6:
				return HttpResponse('NJATH Completed')

			user_info.current_level_score = user_info.current_level * minumum_level_points
			user_info.current_level_opened_questions = 0
			user_info.current_level_answered_questions = 0
			user_info.save()
		return HttpResponseRedirect(reverse('game:profile'))	
	else:
		return HttpResponseRedirect(reverse('users:login'))



def leaderboard(request):
	users = UserInfo.objects.select_related('user').filter(disqualified=False).order_by('total_score')
	return render(request, 'game/leaderboard.html', {'users' : users})
			


def rules(request):
	return render(request,'game/rules.html')



def profile(request):	
	if not request.user.is_authenticated():
		login_url = reverse('users:login')
		profile_url = reverse('game:profile')
		messages.success(request, 'You need to log in first')
		return HttpResponseRedirect(login_url+'?next='+profile_url)

	username = request.user
	user = User.objects.get(username=username)
	user_info = UserInfo.objects.get(user=user)

	questions = Questions.objects.filter(level=user_info.current_level)
	answered_questions = set(UserAnswers.objects.filter(user=user,correct_answer=True,question__in=questions).values_list('question_id',flat=True))
	opened_questions = set(QuestionOpened.objects.filter(user=user,question__in=questions).values_list('question_id',flat=True))

	context = {
		'user_info' : user_info,
		'answered_questions' : answered_questions,
		'opened_questions' : opened_questions,
		'questions' : questions,
		'answered_count' : len(answered_questions),
		'opened_count' : len(opened_questions),
	}

	return render(request, 'game/profile.html',context)



def open_question(request, question_slug):
	if not request.user.is_authenticated():
		login_url = reverse('users:login')
		question_url = reverse('game:question',args=[question_id])
		messages.success(request, 'You need to log in first')
		return HttpResponseRedirect(login_url+'?next='+question_url)

	username = request.user
	user = User.objects.get(username=username)
	user_info = UserInfo.objects.get(user=user)

	try:
		question = Questions.objects.get(slug=question_slug,level=user_info.current_level)
		try:
			question_opened = QuestionOpened.objects.get(user=user,question=question)
		except QuestionOpened.DoesNotExist:
			user_info.current_level_score -= question.penalty
			user_info.current_level_opened_questions += 1
			if user_info.current_level_score < 0:
				messages.warning(request, 'Not enough User Level Score to Unlock')
				return HttpResponseRedirect(reverse('game:profile'))
			question_opened = QuestionOpened.objects.create(user=user,question=question)
			user_info.save()
	except Questions.DoesNotExist:
		messages.success(request, 'Invalid Question Given')
		return HttpResponseRedirect(reverse('game:profile'))

	try:
		question_image = QuestionImage.objects.get(question=question)
	except QuestionImage.DoesNotExist:
		question_image = None

	context = {
		'user_info' : user_info,
		'question' : question,
		'question_image' : question_image,
	}

	return render(request,'game/question.html', context	)



@ajax
def check_answer(request):
	if not request.user.is_authenticated():
		login_url = reverse('users:login')
		profile_url = reverse('game:profile')
		redirect_url = login_url+'?next='+profile_url
		messages.success(request, 'You need to log in first')
		return {'error': False, 'redirect' : redirect_url}


	question_slug = request.POST.get('question_slug','').strip().rstrip()
	answer = request.POST.get('answer','').strip().rstrip()
	username = request.user
	user = User.objects.get(username=username)

	try:
		question = Questions.objects.get(slug=question_slug)
	except Questions.DoesNotExist:
		messages.warning(request, 'Not a valid question')
		return {'error':False, 'redirect' : reverse('game:profile')}


	if answer.lower() != question.answer:
		user_answer = UserAnswers.objects.create(user=user,question=question,correct_answer=False,answer=answer)
		return {'error':True, 'error_info' : 'Incorrect Answer'}
	else:
		user_info = UserInfo.objects.get(user=user)
		try:
			user_answer = UserAnswers.objects.get(user=user,question=question,correct_answer=True,answer=answer)
			message = "<p align='center'>Correct Answer</p><p align='center'>But You already answered it !!!</p>"
		except UserAnswers.DoesNotExist:
			user_answer = UserAnswers.objects.create(user=user,question=question,correct_answer=True,answer=answer)
			user_info.total_score += question.score
			user_info.current_level_score += question.score
			user_info.current_level_answered_questions += 1
			user_info.save()
			message =  "<p align='center'>Correct Answer</p><p align='center'>Great!!!!!!</p>"
		messages.success(request, message ,extra_tags='html_safe')
		return {'error':False, 'redirect' : reverse('game:profile')}		










# def home(request):
# 	if not request.user.is_authenticated():
# 		login_url = reverse('users:login')
# 		home_url = reverse('game:home')
# 		messages.success(request, 'You need to log in first')
# 		return HttpResponseRedirect(login_url+'?next='+home_url)

# 	username = request.user
# 	user = User.objects.get(username=username)
# 	user_info = UserInfo.objects.get(user=user)
# 	question_ids = Questions.objects.filter(level=user_info.current_level).order_by('id').values_list('id',flat=True)
# 	answered_questions = set(UserAnswers.objects.filter(user=user,correct_answer=True).values_list('question_id', flat=True))
# 	opened_questions =  set(QuestionOpened.objects.filter(user=user).values_list('question_id', flat=True))

# 	question = Questions.objects.get(id=question_ids[0])
# 	try:
# 		question_image = QuestionImage.objects.get(question = question)
# 	except QuestionImage.DoesNotExist:
# 		question_image = None

# 	try:
# 		question_opened = QuestionOpened.objects.get(user=user,question=question)
# 	except QuestionOpened.DoesNotExist:
# 		question_opened = QuestionOpened.objects.create(user=user, question=question)


# 	context = {
# 		'user_info' : user_info,
# 		'question_ids' : question_ids,
# 		'answered_questions' : answered_questions,
# 		'opened_questions' : opened_questions,
# 		'question' : question,
# 		'question_image' : question_image
# 	}
# 	return render(request, 'game/home.html', context)






# this function shows all the info of the user
# like all questions level opened answered unopened 

# s.no. question no. level status score
# def profile(request):
# 	if not request.user.is_authenticated():
# 		login_url = reverse('users:login')
# 		profile_url = reverse('game:profile')
# 		messages.success(request, 'You need to log in first')
# 		return HttpResponseRedirect(login_url+'?next='+profile_url)

# 	username = request.user
# 	user = User.objects.get(username=username)
# 	user_info = UserInfo.objects.get(user=user)
# 	questions = Questions.objects.all().order_by('level','id')
# 	answered_questions_ids = set(UserAnswers.objects.filter(user=user).values_list('question_id',flat=True))
# 	opened_questions_ids = set(QuestionOpened.objects.filter(user=user).values_list('question_id',flat=True))
# 	levels = UserLevelProgress.objects.filter(user=user)
# 	levels_count = levels.count()

# 	question_answered = 0
# 	# calculate question_answered for last level if that level has not been completed or submitted 
# 	# as only progress of those level is saved for whom next level button is pressed from frontend 
# 	if levels_count < max_levels:
# 		question_answered = UserAnswers.objects.filter(user=user,question__level=user_info.current_level,correct_answer=True).aggregate(answers=Count('question'))['answers']
# 	context = {
# 		'answered_questions_ids' : answered_questions_ids,
# 		'opened_questions_ids' : opened_questions_ids,
# 		'questions' : questions,
# 		'user_info' : user_info,
# 		'levels' : levels,
# 		'user' : user,
# 		'levels_count' : levels_count,
# 		'max_levels' : max_levels,
# 		'question_answered' : question_answered
# 	}
# 	return render(request, 'game/profile.html', context)




# @ajax
# def get_question(request):
# 	if not request.user.is_authenticated():
# 		login_url = reverse('users:login')
# 		home_url = reverse('game:home')
# 		redirect = login_url + '?next=' + home_url
# 		return ({'error':True, 'redirect':redirect, 'error_info':'Anonnymous User'})

# 	question_id = request.POST.get('question_id',None)
# 	user = User.objects.get(username=username)
# 	try:
# 		question = Questions.objects.get(id=question_id)
# 		try:
# 			question_opened = QuestionOpened.objects.get(user=user, question=question)
# 		except QuestionOpened.DoesNotExist:
# 			question_opened = QuestionOpened.objects.create(user=user, question=question)
# 			user_info = UserInfo.objects.get(user=user)
# 			user_info.level_score -= question.penalty
# 			if user_info.level_score < 0:
# 				return {'error' : True, 'error_info' : 'Not enough Level Score to Open the question'}
# 			user_info.total_score -= question.penalty
# 			user_info.save()

# 			result = {
# 				'error' : False,
# 				'question' : question.question,
# 				'level_score':user_info.level_score,
# 				'total_score' : user_info.total_score,
# 			}
# 			return result
# 	except Questions.DoesNotExist:
# 		return ({'error':True, 'error_info':'No Such Question'})







# def add_opened_question(user, question):
# 	pass






