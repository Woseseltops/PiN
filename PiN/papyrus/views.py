from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import PapyrusSide, Papyrus

class PapyrusSideListView(ListView):
    model = PapyrusSide
    template_name = 'papyrus/papyrus_side_list.html'
    context_object_name = 'papyrus_sides'

# Create your views here.

class PapyrusDetailView(DetailView):
    model = Papyrus
    template_name = 'papyrus/papyrus_detail.html'
    context_object_name = 'papyrus_detail'
