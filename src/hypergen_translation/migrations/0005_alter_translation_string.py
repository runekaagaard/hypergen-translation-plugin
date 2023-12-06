# Generated by Django 4.2.8 on 2023-12-06 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hypergen_translation', '0004_delete_translationstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translation',
            name='string',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hypergen_translation.string', unique=True),
        ),
    ]
