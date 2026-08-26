from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("website", "0007_website_settings_hero_images")]
    operations = [
        migrations.AddField(model_name="blogpost", name="linkedin_published", field=models.BooleanField(default=False, editable=False)),
        migrations.AddField(model_name="blogpost", name="linkedin_post_id", field=models.CharField(blank=True, editable=False, max_length=255)),
        migrations.AddField(model_name="blogpost", name="linkedin_post_url", field=models.URLField(blank=True, editable=False)),
        migrations.AddField(model_name="blogpost", name="linkedin_published_at", field=models.DateTimeField(blank=True, editable=False, null=True)),
        migrations.AddField(model_name="blogpost", name="linkedin_last_error", field=models.TextField(blank=True, editable=False)),
        migrations.AddField(model_name="blogpost", name="linkedin_publish_attempts", field=models.PositiveIntegerField(default=0, editable=False)),
        migrations.CreateModel(name="LinkedInConnection", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("access_token", models.TextField()), ("expires_at", models.DateTimeField()), ("member_id", models.CharField(max_length=255)), ("member_name", models.CharField(blank=True, max_length=255)), ("member_picture", models.URLField(blank=True)), ("connected_at", models.DateTimeField(editable=False, auto_now_add=True)), ("last_sync_at", models.DateTimeField(blank=True, null=True)), ("last_error", models.TextField(blank=True))]),
        migrations.CreateModel(name="LinkedInPost", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("linkedin_id", models.CharField(max_length=255, unique=True)), ("text", models.TextField()), ("published_at", models.DateTimeField()), ("linkedin_url", models.URLField(blank=True)), ("image_url", models.URLField(blank=True)), ("author_name", models.CharField(blank=True, max_length=255)), ("author_picture", models.URLField(blank=True)), ("synced_at", models.DateTimeField(auto_now=True))]),
    ]
