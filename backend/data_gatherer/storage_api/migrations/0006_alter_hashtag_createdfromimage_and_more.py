# Generated by Django 4.2.14 on 2024-08-02 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage_api', '0005_rename_iguser_userhashtaguse_iguser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='createdFromImage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='storage_api.image'),
        ),
        migrations.AlterField(
            model_name='iguser',
            name='createdFromImage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='storage_api.image'),
        ),
        migrations.AlterUniqueTogether(
            name='userhashtaguse',
            unique_together={('image', 'hashtag', 'igUser', 'project')},
        ),
    ]
