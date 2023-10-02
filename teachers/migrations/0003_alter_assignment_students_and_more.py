# Generated by Django 4.2.5 on 2023-10-02 00:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teachers', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='students',
            field=models.ManyToManyField(through='teachers.AssignmentEnrollment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='assignmentenrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='grade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='students',
            field=models.ManyToManyField(through='teachers.LessonEnrollment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lessonenrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='students',
            field=models.ManyToManyField(through='teachers.QuizEnrollment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='quizenrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
