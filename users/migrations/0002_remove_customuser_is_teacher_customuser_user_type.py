# Generated by Django 4.2.5 on 2023-10-01 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_teacher',
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('student', 'Student'), ('teacher', 'Teacher')], default='student', max_length=10),
        ),
    ]