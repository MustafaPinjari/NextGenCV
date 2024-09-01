# urls.py in your app directory (e.g., myapp/urls.py)

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
]+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
