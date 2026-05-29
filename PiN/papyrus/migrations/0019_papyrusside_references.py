from django.db import migrations, models


def copy_reference_to_references(apps, schema_editor):
    PapyrusSide = apps.get_model('papyrus', 'PapyrusSide')
    for side in PapyrusSide.objects.exclude(reference__isnull=True):
        side.references.add(side.reference_id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('papyrus', '0018_papyrus_provenance_short_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='papyrusside',
            name='references',
            field=models.ManyToManyField(blank=True, to='papyrus.reference'),
        ),
        migrations.RunPython(copy_reference_to_references, noop_reverse),
        migrations.RemoveField(
            model_name='papyrusside',
            name='reference',
        ),
    ]
