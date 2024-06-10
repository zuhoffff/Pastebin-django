from django.urls import path
# from .get_text.get_text import get_text
from pastebin_main_app.views import SubmitTextView
from pastebin_main_app.get_text.get_text import get_text

urlpatterns = [
    # path('', HomeView.as_view(), name='home'),
    path('', SubmitTextView.as_view(), name='submit_text'),
    path('paste/<str:url>/',get_text, name='get_text')
]