from django.contrib import admin

# Register your models here.
# i.e., import the tables you create
from .models import Utterance, GeneratedUtterances

# NOTE
# registering the tables allows access to them on the admin site that comes with django
admin.site.register(Utterance)
admin.site.register(GeneratedUtterances)
