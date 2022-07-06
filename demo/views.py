from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

from utils.gen import UtteranceGenerator
from .models import Utterance, GeneratedUtterances


# Design
# - index - displays utterances that we can generate from.
# - generated - displays generated utterances. (in the backend, each generation is entered into the Generated Utterances table.)
# - export - displays selected utterances with an export button (export behavior to be defined).


def index(request):
    '''display list of utterances in Utterance table.
    '''
    try:
        # access all objects in Utterance table
        utterances = Utterance.objects.all()

        # load html template
        template = loader.get_template('demo/index.html')

        # provide access to files in this function
        context = { 'utterances' : utterances }

    except Utterance.DoesNotExist:
        raise Http404("Error: no utterances have been stored yet.")

    return HttpResponse(template.render(context, request))


def detail(request, utterance_id):
    '''return the generated utterances in simple list view.
    '''
    try:
        utterance = Utterance.objects.get(pk=utterance_id).utterance_text
        generated = UtteranceGenerator(utterance).generate()

        for g in generated:
            newutterance = GeneratedUtterances(seed=utterance, generated_utterance=g)
            newutterance.save()

        template  = loader.get_template('demo/detail.html')
        context   = { 'generated' : generated }

    except Utterance.DoesNotExist:
        raise Http404("Error: This utterance does not exist so no additional utterances could \
                      be generated.")

    return HttpResponse(template.render(context, request))


def form(request):
    '''display form to enter an utternace.
    '''
    #TODO
    return HttpResponse("TODO form")


def output(request):
    '''display generated utterances using generate() from the UtteranceGenerator class.
    '''
    #TODO
    return HttpResponse("TODO output")



