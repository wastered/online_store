import os

from celery import Celery

# задать стандартный модуль настроек Django
# для программы 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
app = Celery('server')

# Настройка Celery с использованием конфигурации из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически искать задачи в зарегистрированных приложениях
app.autodiscover_tasks()
