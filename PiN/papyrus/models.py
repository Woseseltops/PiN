from django.db import models

class Material(models.Model):
    name = models.CharField(max_length=100)

class Shape(models.Model):
    name = models.CharField(max_length=100)

class Language(models.Model):
    name = models.CharField(max_length=100)

class Genre(models.Model):
    name = models.CharField(max_length=100)

class Provenance(models.Model):
    name = models.CharField(max_length=100)

class Publication(models.Model):
    content = models.TextField()

class Papyrus(models.Model):
    inventory_number = models.CharField(max_length=100)
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)
    shape = models.ForeignKey(Shape, on_delete=models.DO_NOTHING)
    finding_location = models.CharField(max_length=255)
    current_location = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "papyri"

class PapyrusSide(models.Model):
    papyrus = models.ForeignKey(Papyrus, related_name='sides', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)
    date = models.DateField()
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    content = models.TextField()
    parallel = models.BooleanField(default=False)
    flesh = models.BooleanField(default=False)
    concave = models.BooleanField(default=False)
    publication = models.ForeignKey(Publication, on_delete=models.DO_NOTHING, null=True, blank=True)
    links = models.JSONField(null=True, blank=True)

class Image(models.Model):
    papyrus_side = models.ForeignKey(PapyrusSide, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='papyrus_images/')
