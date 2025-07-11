from django.db import models

class Material(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Shape(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Provenance(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Publication(models.Model):
    content = models.TextField()

    def __str__(self):
        return self.content

class FindingLocation(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class CurrentLocation(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Papyrus(models.Model):
    inventory_number = models.CharField(max_length=100)
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)
    shape = models.ForeignKey(Shape, on_delete=models.DO_NOTHING)

    # Commented out for migration reasons, can be removed later
    # finding_location = models.CharField(max_length=255, null=True, blank=True)
    # current_location = models.CharField(max_length=255, null=True, blank=True)

    finding_location = models.ForeignKey(FindingLocation, on_delete=models.DO_NOTHING, null=True, blank=True)
    current_location = models.ForeignKey(CurrentLocation, on_delete=models.DO_NOTHING, null=True, blank=True)


    class Meta:
        verbose_name_plural = "papyri"

    def __str__(self):
        return f'{self.inventory_number} - {self.material} - {self.shape}'

class Dimension(models.Model):
    item = models.ForeignKey(Papyrus, related_name='dimensions', on_delete=models.CASCADE)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)

class Link(models.Model):
    item = models.ForeignKey(Papyrus, related_name='links', on_delete=models.CASCADE)
    url = models.URLField()
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.url} - {self.description}'

class PapyrusSide(models.Model):
    papyrus = models.ForeignKey(Papyrus, related_name='sides', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)
    year = models.IntegerField(null=True, blank=True)
    year_start = models.IntegerField(null=True, blank=True)
    year_end = models.IntegerField(null=True, blank=True)
    specific_date = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    parallel = models.BooleanField(default=False)
    flesh = models.BooleanField(default=False)
    concave = models.BooleanField(default=False)
    publication = models.ForeignKey(Publication, on_delete=models.DO_NOTHING, null=True, blank=True)
    links = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.papyrus.inventory_number} - {self.title} - {self.language}'

class Image(models.Model):
    papyrus_side = models.ForeignKey(PapyrusSide, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='papyrus_images/')
    credit = models.CharField(max_length=255, null=True, blank=True)
