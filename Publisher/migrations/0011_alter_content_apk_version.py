# Generated by Django 5.0.4 on 2024-07-03 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Publisher', '0010_alter_content_options_content_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='apk_version',
            field=models.CharField(default='1.0.0', max_length=20, null=True),
        ),
    ]
