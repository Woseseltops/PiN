from django.shortcuts import render
from django.views.generic import ListView
from .models import PapyrusSide

class PapyrusSideListView(ListView):
    model = PapyrusSide
    template_name = 'papyrus/papyrus_side_list.html'
    context_object_name = 'papyrus_sides'

# Create your views here.
