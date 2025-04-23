from django.contrib import admin
from .models import Papyrus, PapyrusSide, Material, Shape, Language, Genre, Publication, Image

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

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    search_fields = ['content']

class PapyrusSideInline(admin.StackedInline):
    model = PapyrusSide
    extra = 1  # Number of empty forms to display
    autocomplete_fields = ['language', 'genre', 'publication']

@admin.register(Papyrus)
class PapyrusAdmin(admin.ModelAdmin):
    autocomplete_fields = ['material', 'shape']
    inlines = [PapyrusSideInline]

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('papyrus_side', 'image')