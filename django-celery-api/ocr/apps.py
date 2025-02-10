import os

from django.apps import AppConfig
from django.conf import settings
from django.db.backends.signals import connection_created
from django.dispatch import receiver


class OcrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = settings.APP_NAME

    def ready(self):
        @receiver(connection_created, dispatch_uid="setup_sqlite_once")
        def setup_sqlite_pragmas(sender, connection, **kwargs):
            if connection.vendor == "sqlite":
                with connection.cursor() as cursor:
                    cursor.execute("PRAGMA journal_mode=wal;")
                    cursor.execute("PRAGMA busy_timeout=5000;")
