BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://'

CELERY_TASK_SERIALIZER='json',
CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
CELERY_RESULT_SERIALIZER='json',
# CELERY_TIMEZONE='Europe/Oslo',
CELERY_ENABLE_UTC=True,


CELERY_ROUTES = {
    'tasks.add': 'low-priority',
}

CELERY_ANNOTATIONS = {
    'tasks.add': {'rate_limit': '10/m'}
}

