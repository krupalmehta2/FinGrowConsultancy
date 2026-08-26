from django.db import migrations, models


def normalize_category_order(apps, schema_editor):
    ServiceCategory = apps.get_model("website", "ServiceCategory")
    categories = list(ServiceCategory.objects.order_by("display_order", "name", "pk"))
    for position, category in enumerate(categories, start=1):
        category.display_order = position
        category.save(update_fields=["display_order"])


class Migration(migrations.Migration):
    dependencies = [("website", "0010_alter_servicecategory_options_service_icon_and_more")]

    operations = [
        migrations.AlterField(
            model_name="servicecategory",
            name="display_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Use 1 for the first category, 2 for the second, 3 for the third, and so on. Lower numbers appear first.",
            ),
        ),
        migrations.RunPython(normalize_category_order, migrations.RunPython.noop),
    ]