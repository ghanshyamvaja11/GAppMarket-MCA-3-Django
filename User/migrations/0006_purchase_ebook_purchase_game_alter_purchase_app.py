# Generated by Django 5.0.4 on 2024-07-03 12:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Publisher', '0015_content_content_type'),
        ('User', '0005_review_rating_delete_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='ebook',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Publisher.ebook'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Publisher.game'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='app',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Publisher.app'),
        ),
    ]
