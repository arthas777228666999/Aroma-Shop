# Generated by Django 5.1.6 on 2025-05-12 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_scentofmonth'),
    ]

    operations = [
        migrations.AddField(
            model_name='productperfume',
            name='is_scent_of_month',
            field=models.BooleanField(default=False),
        ),
    ]
