# Generated by Django 4.2.7 on 2023-11-07 01:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0020_attempt_completed_timestamp_attempt_is_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='teachers.teacher'),
        ),
    ]