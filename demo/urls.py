# map urls to view functions
from django.urls import path
from . import views

# URLConf (or url configuration)
# purpose is to map the url pattern (the webpage at this endpoint) to the view (to a python function that returns some data on the webpage)
urlpatterns = [
    path('', views.index, name="index"),
    path('<int:utterance_id>/', views.detail, name="detail"),
    path('form/', views.form, name="form"),
    path('output/', views.output, name="output")
]
