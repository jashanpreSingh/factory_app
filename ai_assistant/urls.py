from django.urls import path

from .views import AssistantChatAPI


urlpatterns = [
    path('assistant/chat/', AssistantChatAPI.as_view(), name='ai-assistant-chat'),
]
