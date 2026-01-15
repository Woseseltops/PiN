from .models import Editor
from django.contrib import admin
from django import forms
from .models import Papyrus, PapyrusSide, Material, Shape, Language, Genre, Reference, Image, Dimension, Link, FindingLocation, CurrentLocation, Page

@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Page._meta.fields]

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ['content']

@admin.register(FindingLocation)
class FindingLocationAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(CurrentLocation)
class CurrentLocationAdmin(admin.ModelAdmin):
    search_fields = ['name']

class DimensionInline(admin.TabularInline):  # or admin.StackedInline
    model = Dimension
    extra = 0  # how many empty forms to show
    min_num = 1

class LinkInline(admin.TabularInline):
    model = Link
    extra = 1  # Number of empty forms to display

class PapyrusSideForm(forms.ModelForm):
    class Meta:
        model = PapyrusSide
        exclude = []
        labels = {
            'parallel': 'Parallel to the fibres',
            'editors': 'Editor(s)',
        }

class PapyrusSideInline(admin.StackedInline):
    model = PapyrusSide
    form = PapyrusSideForm
    extra = 1  # Number of empty forms to display
    autocomplete_fields = ['language', 'genre', 'reference']
    exclude = []


# Custom filter for published status
class PublishedListFilter(admin.SimpleListFilter):
    title = 'Published'
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(sides__published=True).distinct()
        if value == 'no':
            return queryset.exclude(sides__published=True).distinct()
        return queryset

@admin.register(Papyrus)
class PapyrusAdmin(admin.ModelAdmin):
    autocomplete_fields = ['material', 'shape', 'finding_location', 'current_location']
    inlines = [DimensionInline, PapyrusSideInline, LinkInline]
    list_display = ('inventory_number', 'current_location', 'published_column', 'material', 'shape')
    list_filter = ('current_location', 'material', 'shape', PublishedListFilter)

    def published_column(self, obj):
        return any(side.published for side in obj.sides.all())
        
    published_column.boolean = True
    published_column.short_description = 'Published'

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('papyrus_side', 'image')