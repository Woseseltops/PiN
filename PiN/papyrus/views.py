from django.shortcuts import render
from django.views.generic import ListView
from .models import PapyrusSide, Papyrus

class PapyrusSideListView(ListView):
    model = PapyrusSide
    template_name = 'papyrus/papyrus_side_list.html'
    context_object_name = 'papyrus_sides'

class PapyrusDetailView(ListView):
    model = Papyrus
    template_name = 'papyrus/papyrus_detail.html'
    context_object_name = 'papyrus'

    def get_queryset(self):
        return Papyrus.objects.filter(id=self.kwargs['pk'])[0]