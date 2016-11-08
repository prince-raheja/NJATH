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



MINIMUM_QUESTION_ANSWERED = 6
MINIMUM_LEVEL_POINTS = 40
MAX_LEVELS = 6

def home(request):
    if not request.user.is_authenticated():
        login_url = reverse('users:login')
        home_url = reverse('game:home')
        messages.success(request, 'You need to log in first')
        return HttpResponseRedirect(login_url+'?next='+home_url)

    username = request.user
    user = User.objects.get(username=username)
    if not user.is_active:
        return HttpResponseRedirect(reverse('users:activation_pending'))
    user_info = UserInfo.objects.get(user=user)
    question_ids = Questions.objects.filter(level=user_info.current_level).order_by('id').values_list('id',flat=True)
    answered_questions = set(UserAnswers.objects.filter(user=user,correct_answer=True).values_list('question_id', flat=True))
    opened_questions =  set(QuestionOpened.objects.filter(user=user).values_list('question_id', flat=True))

    question = Questions.objects.get(id=question_ids[0])
    try:
        question_image = QuestionImage.objects.get(question = question)
    except QuestionImage.DoesNotExist:
        question_image = None

    try:
        question_opened = QuestionOpened.objects.get(user=user,question=question)
    except QuestionOpened.DoesNotExist:
        question_opened = QuestionOpened.objects.create(user=user, question=question)


    context = {
        'user_info' : user_info,
        'question_ids' : question_ids,
        'answered_questions' : answered_questions,
        'opened_questions' : opened_questions,
        'question' : question,
        'question_image' : question_image
    }
    return render(request, 'game/home.html', context)



def next_level(request):
    if request.user.is_authenticated():
        user = User.objects.get(username=username)
        if not user.is_active:
            return HttpResponseRedirect(reverse('users:activation_pending'))
        user_info = UserInfo.objects.get(user=user)
        question_answered = QuestionOpened.objects.filter(user=user, question__level=user_info.current_level).aggregate(total_opened=Count('question'))
        if question_answered < MINIMUM_QUESTION_ANSWERED:
            messages.success(request, 'Answer 6 questions in Current Level First')
            return HttpResponseRedirect(reverse('game:home'))
        try:
            user_level_score = UserLevelProgress.objects.get(user=user, level=user_info.current_level)
            return HttpResponse('Already Played that level')
        except UserLevelProgress.DoesNotExist:
            total_level_score = UserLevelProgress.objects.filter(user=user).aggregate(total_score=Sum('level_score'))['total_score']
            if total_level_score is None:
                total_level_score = 0 

            new_level = UserLevelProgress.objects.create(user=user, level=user_info.current_level, level_score=user_info.total_score-total_level_score)
            user_info.current_level += 1
            user_info.current_level_score = user_info.current_level*MINIMUM_LEVEL_POINTS
            user_info.save()
            return HttpResponseRedirect(reverse('game:home'))
    else:
        return HttpResponseRedirect(reverse('users:login'))



def leaderboard(request):
    users = UserInfo.objects.select_related('user').filter(disqualified=False).order_by('-total_score')
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
    if not user.is_active:
        return HttpResponseRedirect(reverse('users:activation_pending'))
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
    if not user.is_active:
        return HttpResponseRedirect(reverse('users:activation_pending'))
    user_info = UserInfo.objects.get(user=user)

    try:
        question = Questions.objects.get(slug=question_slug,level=user_info.current_level)
        try:
            question_opened = QuestionOpened.objects.get(user=user,question=question)
        except QuestionOpened.DoesNotExist:
            # user_info.total_score -= question.penalty
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
    return render(request,'game/question.html', context )


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
    if not user.is_active:
        return {'error':False, 'redirect' : reverse('users:activation_pending')}
    try:
        question = Questions.objects.get(slug=question_slug)
    except Questions.DoesNotExist:
        messages.warning(request, 'Not a valid question')
        return {'error':False, 'redirect' : reverse('game:leaderboard')}    
    if answer.lower() != question.answer:
        user_answer = UserAnswers.objects.create(user=user,question=question,correct_answer=False,answer=answer)
        return {'error':True, 'error_info' : 'Incorrect Answer'}
    else:
        user_info = UserInfo.objects.get(user=user)
        try:
            user_answer = UserAnswers.objects.get(user=user,question=question,correct_answer=True,answer=answer)
        except UserAnswers.DoesNotExist:
            user_answer = UserAnswers.objects.create(user=user,question=question,correct_answer=True,answer=answer)
            user_info.total_score += question.score
            user_info.current_level_score += question.score
            user_info.save()
        message =  "<p align='center'>Correct Answer</p><p align='center'>Great!!!!!!</p>"
        messages.success(request, message ,extra_tags='html_safe')
        return {'error':False, 'redirect' : reverse('game:profile')}