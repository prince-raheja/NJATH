from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treasure_hunt.settings')

from django.conf import settings

app = Celery(
		'treasure_hunt',
		broker='redis://localhost:6379/0',
		backend='redis://',
		include=['treasure_hunt.tasks']
	)

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda : settings.INSTALLED_APPS)

app.conf.update(
	CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
	app.start()
