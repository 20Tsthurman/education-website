# Generated by Django 4.2.5 on 2023-10-03 03:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_customuser_is_teacher_customuser_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]