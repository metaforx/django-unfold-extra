import djangocms_text.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("testapp", "0004_document"),
    ]

    operations = [
        migrations.CreateModel(
            name="Note",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("body", djangocms_text.fields.HTMLField(blank=True)),
            ],
        ),
    ]
