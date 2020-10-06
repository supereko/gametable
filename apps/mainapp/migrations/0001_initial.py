# Generated by Django 3.0.6 on 2020-09-15 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20, verbose_name='название игры')),
                ('desc', models.TextField(max_length=1000, verbose_name='краткое описание игры')),
                ('begin', models.DateTimeField(auto_now_add=True, verbose_name='время начала игры')),
                ('end', models.DateTimeField(auto_now_add=True, verbose_name='время окончания игры')),
            ],
        ),
    ]