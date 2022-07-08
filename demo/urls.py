from django.urls import path
from . import views

# URLConf (or url configuration)
# purpose is to map the url pattern (the webpage at this endpoint) to the view (to a python function that returns some data on the webpage)
urlpatterns = [
    path('input/', views.input, name="input"),                        # add a new utterance to the database table
    path('', views.index, name="index"),                              # displays seed utterances
    path('<int:utterance_id>/', views.form, name="form"),             # for the seed utterance, displays the generated utterances to select which to export
    path('export/<int:utterance_id>/', views.export, name="export")   # return the json with the generated utterances selected for export
]
