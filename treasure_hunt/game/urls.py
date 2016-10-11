from django.conf.urls import url

from game.views import home, leaderboard, rules, profile, open_question, next_level, check_answer

app_name = 'game'

urlpatterns = [
	url(r'^$', home, name='home'),
	url(r'^leaderboard$',leaderboard, name='leaderboard'),
	url(r'^profile$', profile, name='profile'),
	url(r'^rules$', rules, name='rules'),
	url(r'^question/(?P<question_slug>[a-zA-Z0-9-]+)$', open_question, name='question'),
	url(r'^next_level$', next_level, name='next_level'),
	url(r'^check_answer$', check_answer, name='check_answer')
	# url(r'^question/(?P<question_slug>^[a-zA-Z0-9-]+)$', open_question, name='question'),
]