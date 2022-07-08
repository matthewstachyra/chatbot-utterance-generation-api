import json

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

from utils.gen import UtteranceGenerator
from .models import SeedUtterance, GeneratedUtterances


# Routing
# input - form to add seed utterance.
# index - display seed utterances to generate from.
# form - displays generated utterances for the seed utterance to select which to export.


def input(request):
    '''provide form to input a new seed utterance.
    '''
    try:
        template = loader.get_template('demo/input.html')

    except:
        raise Http404("Error: template is unavailable.")

    return HttpResponse(template.render({}, request))


def index(request):
    '''display list of utterances in Utterance table.
    '''
    try:
        new = SeedUtterance(seed_text=request.POST['seed'])
        new.save()

    except Exception:
        pass # allows access to /demo without passing through /demo/input first

    try:
        utterances = SeedUtterance.objects.all()

    except SeedUtterance.DoesNotExist:
        raise Http404("Error: no utterances have been stored yet.")

    finally:
        template = loader.get_template('demo/index.html')
        context = { 'utterances' : utterances }

    return HttpResponse(template.render(context, request))


def form(request, utterance_id):
    '''return the generated utterances for the seed text in a simple form
    where you select which to save -- to be exported.
    '''
    try:
        seed_utterance = SeedUtterance.objects.get(pk=utterance_id)
        generated      = UtteranceGenerator(seed_utterance.seed_text).generate()

        for g in generated:
            if not GeneratedUtterances.objects.filter(generated_text=g):
                new = GeneratedUtterances(seed_utterance=seed_utterance, generated_text=g)
                new.save()

        generated_utterances = GeneratedUtterances.objects.filter(seed_utterance=seed_utterance)
        context = { 'seed_utterance' : seed_utterance,
                    'generated_utterances' : generated_utterances
                   }
        template = loader.get_template('demo/form.html')

    except SeedUtterance.DoesNotExist:
        raise Http404("Error: This utterance does not exist so no additional utterances could \
                      be generated.")

    return HttpResponse(template.render(context, request))


def export(request, utterance_id):
    '''export the saved generated utterances.
    '''
    try:
        seed_utterance = SeedUtterance.objects.get(pk=utterance_id)
        generated_utterances = request.POST.getlist('generated')
        json_data['seed'] = seed_utterance.seed_text
        json_data['generated'] = generated_utterances.split()
        json = json.dumps(json_data)
        print(json)

    except:
        raise Http404("Error exporting data from form.")

    return HttpResponse(for_export)


