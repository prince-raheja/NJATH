# from celery import Celery
# # celeryconfig

# app = Celery('tasks',broker='redis://localhost:6379/0', backend='redis://')
# # app.config_from_object('celeryconfig')

# app.conf.update(
# 	CELERY_TASK_SERIALIZER='json',
# 	CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
# 	CELERY_RESULT_SERIALIZER='json',
# 	# CELERY_TIMEZONE='Europe/Oslo',
# 	CELERY_ENABLE_UTC=True,

# )

# @app.task
# def add(x,y):
# 	return x+y



from __future__ import absolute_import

from treasure_hunt.celery import app


@app.task
def add(x,y):
	return x+y


@app.task
def mul(x,y):
	return x*y


@app.task
def xsum(numbers):
	return sum(numbers)