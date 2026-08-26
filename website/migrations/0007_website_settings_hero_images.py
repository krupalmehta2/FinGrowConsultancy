from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [("website", "0006_customerprofile")]
    operations = [migrations.AddField(model_name="websitesettings", name="hero_image", field=models.ImageField(blank=True, null=True, upload_to="settings/")), migrations.AddField(model_name="websitesettings", name="about_hero_image", field=models.ImageField(blank=True, null=True, upload_to="settings/"))]
