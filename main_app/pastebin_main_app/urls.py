from django.urls import path
from .views import home
from .submit_text import submit_text
from .get_text import get_text

urlpatterns = [
    path("", home, name='home'),
    path('submit-text/', submit_text, name='submit_text'),
    path('block/<str:url>/',get_text, name='get_text')
]