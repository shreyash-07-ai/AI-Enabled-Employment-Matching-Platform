# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except Exception as e:
    print(f"Warning: Could not import Celery app: {e}")
    __all__ = ()
