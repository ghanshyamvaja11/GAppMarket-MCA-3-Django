# Generated by Django 5.0.4 on 2024-07-03 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Publisher', '0012_alter_content_apk_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='apk_version',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]