# Generated by Django 4.2.14 on 2024-08-03 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage_api', '0007_alter_hashtag_createdfromimage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='isSimilarTo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='storage_api.image'),
        ),
    ]
