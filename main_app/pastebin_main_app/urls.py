from django.urls import path
# from .get_text.get_text import get_text
from pastebin_main_app.submit_text.submit_text_view import SubmitTextView
from .get_text.get_text_view import PasswordPromptView, PasteDetailView

urlpatterns = [
    # path('', HomeView.as_view(), name='home'),
    path('', SubmitTextView.as_view(), name='submit_text'),
    path('paste/<str:slug>/',PasteDetailView.as_view(), name='paste_detail_view'),
    path('paste/<str:slug>/password/', PasswordPromptView.as_view(), name='paste_password_prompt'),
]