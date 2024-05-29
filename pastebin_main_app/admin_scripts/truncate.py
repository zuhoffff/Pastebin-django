from os import environ
from django.db import connection

# TODO: make truncate scripts

def truncate_database():
    with connection.cursor() as cursor:
        cursor.execute(f'TRUNCATE TABLE {environ.get('')} CASCADE;')