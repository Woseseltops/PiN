from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("papyrus", "0008_alter_papyrus_current_location_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Publication",
            new_name="Reference",
        ),
        migrations.RenameField(
            model_name="papyrusside",
            old_name="publication",
            new_name="reference",
        ),
    ]
