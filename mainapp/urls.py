from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name='index'),
    path('contact', views.contact , name='contact'),
    path('about', views.about , name='about'),
    path('results', views.results , name='results'),
    path('dehaze', views.dehaze , name='dehaze'),
    path('upload', views.upload , name='upload'),
    path('realtime', views.realtime , name='realtime'),
]