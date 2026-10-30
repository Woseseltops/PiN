from .models import Editor
from django.contrib import admin
from django import forms
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile
from io import BytesIO
from PIL import Image as PilImage
from .models import Papyrus, PapyrusSide, Material, Shape, Language, Genre, Reference, Image, Dimension, Link, FindingLocation, CurrentLocation, Page, Download


class DownloadInline(admin.TabularInline):
    model = Download
    extra = 1

@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Page._meta.fields]
    inlines = [DownloadInline]

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

class PapyrusSideForm(forms.ModelForm):
    class Meta:
        model = PapyrusSide
        exclude = []
        labels = {
            'parallel': 'Parallel to the fibres',
            'editors': 'Editor(s)',
        }

class ImageAdminForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = '__all__'

    def clean_image(self):
        uploaded = self.cleaned_data.get('image')
        if not isinstance(uploaded, UploadedFile):
            return uploaded

        uploaded.seek(0)
        with PilImage.open(uploaded) as source:
            if source.format != 'TIFF':
                uploaded.seek(0)
                return uploaded

            source.seek(0)
            mode = 'RGBA' if 'A' in source.getbands() else 'RGB'
            png = BytesIO()
            source.convert(mode).save(png, format='PNG')

        filename = uploaded.name.rsplit('.', 1)[0] + '.png'
        return SimpleUploadedFile(filename, png.getvalue(), content_type='image/png')

class PapyrusSideInline(admin.StackedInline):
    model = PapyrusSide
    form = PapyrusSideForm
    extra = 1  # Number of empty forms to display
    autocomplete_fields = ['languages', 'genre', 'references']
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
    inlines = [DimensionInline, PapyrusSideInline]
    list_display = ('inventory_number', 'current_location', 'published_column', 'material', 'shape')
    list_filter = ('current_location', 'material', 'shape', PublishedListFilter)

    def published_column(self, obj):
        return any(side.published for side in obj.sides.all())
        
    published_column.boolean = True
    published_column.short_description = 'Published'

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('papyrus_side', 'url', 'description')
    search_fields = ('url', 'description', 'papyrus_side__publication', 'papyrus_side__papyrus__inventory_number')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    form = ImageAdminForm
    list_display = ('papyrus_side', 'image', 'local_iiif_info_path')
    search_fields = ('papyrus_side__publication', 'papyrus_side__papyrus__inventory_number')

    def local_iiif_info_path(self, obj):
        return f'/iiif/2/{obj.pk}/info.json' if obj.image else '-'

    local_iiif_info_path.short_description = 'Local IIIF info.json'