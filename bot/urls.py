from django.conf.urls import url
from .views import BotView

urlpatterns = [
    url(r'^XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/?$', BotView.as_view())  #secret url
]
