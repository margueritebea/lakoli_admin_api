import os
from celery import Celery

# On définit le module de réglages par défaut pour le programme 'celery'.
# Ici, on pointe vers settings.py (ta configuration de production/par défaut)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('lakoli_admin_api')

# On utilise une chaîne ici pour que le worker n'ait pas à sérialiser
# l'objet de configuration lors de l'utilisation de Windows.
# Le namespace 'CELERY' signifie que toutes les clés de configuration de Celery
# doivent avoir un préfixe `CELERY_` dans settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charge les tâches (tasks.py) de toutes les applications enregistrées (INSTALLED_APPS).
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')