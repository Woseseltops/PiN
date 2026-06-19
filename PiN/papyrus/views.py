from django.shortcuts import render
from django.views.generic import ListView
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from .models import PapyrusSide, Papyrus, Page, Image


def _get_pillow_image(image_obj):
    from PIL import Image as PilImage

    if not image_obj.image:
        raise Http404("Uploaded image not found")
    return PilImage.open(image_obj.image.path)


def _parse_region(region, width, height):
    if region == 'full':
        return (0, 0, width, height)

    parts = region.split(',')
    if len(parts) != 4:
        raise ValueError("Invalid region parameter")

    x, y, w, h = [int(v) for v in parts]
    if x < 0 or y < 0 or w <= 0 or h <= 0:
        raise ValueError("Invalid region values")

    if x + w > width or y + h > height:
        raise ValueError("Region exceeds image bounds")

    return (x, y, x + w, y + h)


def _parse_size(size, source_width, source_height):
    if size in ['full', 'max']:
        return (source_width, source_height)

    if size.startswith('pct:'):
        percentage = float(size[4:])
        if percentage <= 0:
            raise ValueError("Size percentage must be greater than zero")
        return (
            max(1, round(source_width * (percentage / 100))),
            max(1, round(source_height * (percentage / 100))),
        )

    if size.startswith('!'):
        bounds = size[1:].split(',')
        if len(bounds) != 2:
            raise ValueError("Invalid size parameter")
        max_w, max_h = int(bounds[0]), int(bounds[1])
        if max_w <= 0 or max_h <= 0:
            raise ValueError("Invalid size bounds")
        ratio = min(max_w / source_width, max_h / source_height)
        return (max(1, round(source_width * ratio)), max(1, round(source_height * ratio)))

    parts = size.split(',')
    if len(parts) != 2:
        raise ValueError("Invalid size parameter")

    w_str, h_str = parts
    if w_str and h_str:
        return (int(w_str), int(h_str))

    if w_str:
        target_w = int(w_str)
        if target_w <= 0:
            raise ValueError("Width must be positive")
        ratio = target_w / source_width
        return (target_w, max(1, round(source_height * ratio)))

    if h_str:
        target_h = int(h_str)
        if target_h <= 0:
            raise ValueError("Height must be positive")
        ratio = target_h / source_height
        return (max(1, round(source_width * ratio)), target_h)

    raise ValueError("Invalid size parameter")


def _parse_rotation(rotation):
    if rotation.startswith('!'):
        raise ValueError("Mirroring is not supported")

    value = float(rotation)
    if value < 0 or value > 360:
        raise ValueError("Rotation must be between 0 and 360")
    return value


def iiif_redirect(request, image_id):
    from django.shortcuts import redirect
    return redirect(reverse('iiif_image_info', kwargs={'image_id': image_id}), permanent=False)


def iiif_image_info(request, image_id):
    image_obj = Image.objects.filter(pk=image_id).first()
    if not image_obj or not image_obj.image:
        raise Http404("Image not found")

    with _get_pillow_image(image_obj) as pil_image:
        width, height = pil_image.size

    base_id = request.build_absolute_uri(
        reverse('iiif_image_info', kwargs={'image_id': image_obj.pk})
    ).removesuffix('/info.json')

    data = {
        '@context': 'http://iiif.io/api/image/2/context.json',
        '@id': base_id,
        'protocol': 'http://iiif.io/api/image',
        'width': width,
        'height': height,
        'profile': ['http://iiif.io/api/image/2/level1.json'],
    }
    response = JsonResponse(data)
    response['Content-Type'] = 'application/ld+json'
    response['Access-Control-Allow-Origin'] = '*'
    return response


def iiif_image(request, image_id, region, size, rotation, quality_format):
    image_obj = Image.objects.filter(pk=image_id).first()
    if not image_obj or not image_obj.image:
        raise Http404("Image not found")

    if '.' not in quality_format:
        return HttpResponse('Invalid quality/format', status=400)

    quality, output_format = quality_format.rsplit('.', 1)
    output_format = output_format.lower()
    if output_format not in ['jpg', 'png']:
        return HttpResponse('Unsupported format', status=400)
    if quality not in ['default', 'color', 'gray', 'bitonal']:
        return HttpResponse('Unsupported quality', status=400)

    try:
        with _get_pillow_image(image_obj) as source:
            source_width, source_height = source.size
            crop_box = _parse_region(region, source_width, source_height)
            target_size = _parse_size(size, crop_box[2] - crop_box[0], crop_box[3] - crop_box[1])
            rotation_value = _parse_rotation(rotation)

            transformed = source.crop(crop_box).resize(target_size)

            if rotation_value:
                transformed = transformed.rotate(-rotation_value, expand=True)

            if quality == 'gray':
                transformed = transformed.convert('L')
            elif quality == 'bitonal':
                transformed = transformed.convert('1')

            from io import BytesIO

            buffer = BytesIO()
            save_format = 'JPEG' if output_format == 'jpg' else 'PNG'
            if save_format == 'JPEG' and transformed.mode in ['RGBA', 'LA', 'P']:
                transformed = transformed.convert('RGB')
            transformed.save(buffer, format=save_format)
            image_bytes = buffer.getvalue()
    except ValueError as exc:
        return HttpResponse(str(exc), status=400)

    response = HttpResponse(image_bytes, content_type=f'image/{output_format}')
    response['Access-Control-Allow-Origin'] = '*'
    return response

class PapyrusSideListView(ListView):
    model = PapyrusSide
    template_name = 'papyrus/papyrus_side_list.html'
    context_object_name = 'papyrus_sides'

    def get_queryset(self):
        return PapyrusSide.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_pages'] = Page.objects.order_by('menu_bar_order')
        context['collection_pages'] = Page.objects.filter(collection=True).order_by('menu_bar_order')
        return context

class PapyrusDetailView(ListView):
    model = Papyrus
    template_name = 'papyrus/papyrus_detail.html'
    context_object_name = 'papyrus'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_pages'] = Page.objects.order_by('menu_bar_order')
        context['collection_pages'] = Page.objects.filter(collection=True).order_by('menu_bar_order')
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
    collection_pages = Page.objects.filter(collection=True).order_by('menu_bar_order')
    lang = request.GET.get('lang', 'en')
    return render(request, 'papyrus/page.html', {'page': page, 'menu_pages': menu_pages, 'collection_pages': collection_pages, 'lang': lang})

def home_page_view(request):
    try:
        page = Page.objects.get(is_home=True)
    except Page.DoesNotExist:
        raise Http404("Home page not found")
    menu_pages = Page.objects.order_by('menu_bar_order')
    collection_pages = Page.objects.filter(collection=True).order_by('menu_bar_order')
    lang = request.GET.get('lang', 'en')
    return render(request, 'papyrus/page.html', {'page': page, 'menu_pages': menu_pages, 'collection_pages': collection_pages, 'lang': lang})