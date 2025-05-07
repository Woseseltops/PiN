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

class Papyrus(models.Model):
    inventory_number = models.CharField(max_length=100)
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)
    shape = models.ForeignKey(Shape, on_delete=models.DO_NOTHING)
    finding_location = models.CharField(max_length=255)
    current_location = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "papyri"

    def __str__(self):
        return f'{self.inventory_number} - {self.material} - {self.shape}'

class Dimension(models.Model):
    item = models.ForeignKey(Papyrus, related_name='dimensions', on_delete=models.CASCADE)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
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

    def __str__(self):
        return f'{self.papyrus.inventory_number} - {self.title} - {self.language}'

class Image(models.Model):
    papyrus_side = models.ForeignKey(PapyrusSide, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='papyrus_images/')
    credit = models.CharField(max_length=255, null=True, blank=True)
