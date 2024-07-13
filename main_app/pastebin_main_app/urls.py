from django.urls import path
from pastebin_main_app.submit_text.submit_text_view import SubmitTextView
from pastebin_main_app.get_text.get_text_view import PasswordPromptView, PasteDetailView, CheckProtection
from pastebin_main_app.homepage.home_view import HomePage
from pastebin_main_app.list_pastes.list_pastes_api_viewset import ListPastesApiSet

urlpatterns = [
    path('/', HomePage.as_view(), name='home'),
    path('', HomePage.as_view(), name='home'),
    path('submit_text/', SubmitTextView.as_view(), name='submit_text'),
    path('submit_text', SubmitTextView.as_view(), name='submit_text'),
    path('paste/<str:slug>/',CheckProtection.as_view(), name='check_protection'),
    path('paste/<str:slug>',CheckProtection.as_view(), name='check_protection'),
    path('paste/<str:slug>/password/', PasswordPromptView.as_view(), name='paste_password_prompt'),
    path('paste/<str:slug>/password', PasswordPromptView.as_view(), name='paste_password_prompt'),
    path('paste/<str:slug>/view/',PasteDetailView.as_view(), name='paste_detail_view'),
    path('paste/<str:slug>/view',PasteDetailView.as_view(), name='paste_detail_view'),

    # API
    path('list_pastes',ListPastesApiSet.as_view({'get': 'list',}), name='list_pastes'),
    path('list_pastes/',ListPastesApiSet.as_view({'get': 'list',}), name='list_pastes'),
]