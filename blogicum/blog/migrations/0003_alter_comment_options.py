# Generated by Django 3.2.16 on 2024-04-22 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20240421_1956'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['created_at'], 'verbose_name': 'комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]