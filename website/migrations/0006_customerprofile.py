from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [("website", "0005_seed_service_categories"), ("auth", "0012_alter_user_first_name_max_length")]
    operations = [migrations.CreateModel(name="CustomerProfile", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("full_name", models.CharField(max_length=150)), ("mobile_number", models.CharField(max_length=30)), ("city", models.CharField(max_length=100)), ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)), ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="customer_profile", to="auth.user"))])]
