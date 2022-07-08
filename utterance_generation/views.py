import logging

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

def demo(request):
    '''display server start up page that links to the demo
    '''
    try:
        template = loader.get_template('demo.html')

    except Exception as e:
        logging.error(e)
        raise Http404("Error: template is unavailable.")

    return HttpReponse(template.render({}, request))
