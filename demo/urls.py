# map urls to view functions
from django.urls import path
from . import views

# URLConf (or url configuration)
# purpose is to map the url pattern (the webpage at this endpoint) to the view (to a python function that returns some data on the webpage)
urlpatterns = [
    path('input', views.input, name="input"),                        # add a new utterance to the database table
    path('', views.index, name="index"),                             # displays seed utterances
    path('<int:utterance_id>/', views.form, name="form"),            # for the seed utterance, displays the generated utterances
    path('<int:utterance_id>/export/', views.export, name="export")
]
