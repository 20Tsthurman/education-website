# Generated by Django 4.2.7 on 2023-11-07 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0021_alter_grade_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='grade',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
