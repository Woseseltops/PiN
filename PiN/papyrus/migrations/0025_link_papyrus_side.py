from django.db import migrations, models
import django.db.models.deletion


def move_links_to_first_side(apps, schema_editor):
    Link = apps.get_model('papyrus', 'Link')
    PapyrusSide = apps.get_model('papyrus', 'PapyrusSide')

    first_side_by_papyrus = {}
    for papyrus_id, side_id in PapyrusSide.objects.order_by('papyrus_id', 'id').values_list('papyrus_id', 'id'):
        first_side_by_papyrus.setdefault(papyrus_id, side_id)

    missing = []
    for link in Link.objects.all().only('id', 'item_id'):
        side_id = first_side_by_papyrus.get(link.item_id)
        if side_id is None:
            missing.append(str(link.id))
            continue

        link.papyrus_side_id = side_id
        link.save(update_fields=['papyrus_side'])

    if missing:
        raise RuntimeError(
            'Cannot migrate Link rows without a PapyrusSide. '
            'Create at least one side for each papyrus first. '
            f'Affected link IDs: {", ".join(missing)}'
        )


def move_links_back_to_papyrus(apps, schema_editor):
    Link = apps.get_model('papyrus', 'Link')
    PapyrusSide = apps.get_model('papyrus', 'PapyrusSide')

    side_to_papyrus = dict(PapyrusSide.objects.values_list('id', 'papyrus_id'))
    for link in Link.objects.all().only('id', 'papyrus_side_id'):
        papyrus_id = side_to_papyrus.get(link.papyrus_side_id)
        if papyrus_id is None:
            continue
        link.item_id = papyrus_id
        link.save(update_fields=['item'])


class Migration(migrations.Migration):

    dependencies = [
        ('papyrus', '0024_papyrusside_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='papyrus_side',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='links',
                to='papyrus.papyrusside',
            ),
        ),
        migrations.RunPython(move_links_to_first_side, move_links_back_to_papyrus),
        migrations.RemoveField(
            model_name='link',
            name='item',
        ),
        migrations.AlterField(
            model_name='link',
            name='papyrus_side',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='links',
                to='papyrus.papyrusside',
            ),
        ),
    ]
