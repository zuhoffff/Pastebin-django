from django.urls import path
# from .get_text.get_text import get_text
from .views import SubmitTextView

urlpatterns = [
    # path('', HomeView.as_view(), name='home'),
    path('', SubmitTextView.as_view(), name='submit_text'),
]