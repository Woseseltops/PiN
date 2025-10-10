from django.shortcuts import render
from django.views.generic import ListView
from django.http import Http404
from .models import PapyrusSide, Papyrus, Page

class PapyrusSideListView(ListView):
    model = PapyrusSide
    template_name = 'papyrus/papyrus_side_list.html'
    context_object_name = 'papyrus_sides'

    def get_queryset(self):
        return PapyrusSide.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_pages'] = Page.objects.order_by('menu_bar_order')
        return context

class PapyrusDetailView(ListView):
    model = Papyrus
    template_name = 'papyrus/papyrus_detail.html'
    context_object_name = 'papyrus'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_pages'] = Page.objects.order_by('menu_bar_order')
        try:
            side_index = int(self.request.GET.get('side', 0))
        except (TypeError, ValueError):
            side_index = 0
        context['side_index'] = side_index
        return context

    def get_queryset(self):
        return Papyrus.objects.filter(id=self.kwargs['pk'])[0]

def page_view(request, page_name):
    try:
        page = Page.objects.get(name=page_name)
    except Page.DoesNotExist:
        raise Http404("Page not found")
    menu_pages = Page.objects.order_by('menu_bar_order')
    lang = request.GET.get('lang', 'en')
    return render(request, 'papyrus/page.html', {'page': page, 'menu_pages': menu_pages, 'lang': lang})

def home_page_view(request):
    try:
        page = Page.objects.get(is_home=True)
    except Page.DoesNotExist:
        raise Http404("Home page not found")
    menu_pages = Page.objects.order_by('menu_bar_order')
    lang = request.GET.get('lang', 'en')
    return render(request, 'papyrus/page.html', {'page': page, 'menu_pages': menu_pages, 'lang': lang})