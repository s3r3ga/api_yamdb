# Generated by Django 2.2.16 on 2022-12-08 19:54

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': ('Категория',),
                'verbose_name_plural': 'Категории',
                'ordering': ('slug',),
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Комментарий')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': ('Комментарий',),
                'verbose_name_plural': 'Комментарии',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': ('Жанр',),
                'verbose_name_plural': 'Жанры',
                'ordering': ('slug',),
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Отзыв')),
                ('score', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальная оценка 1'), django.core.validators.MaxValueValidator(10, message='Максимальная оценка 10')], verbose_name='Оценка')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': ('Отзыв',),
                'verbose_name_plural': 'Отзывы',
                'ordering': ('-score',),
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Название')),
                ('year', models.IntegerField(blank=True, verbose_name='Год издания')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category', to='reviews.Category', verbose_name='Категория')),
                ('genre', models.ManyToManyField(blank=True, related_name='genre', to='reviews.Genre', verbose_name='Жанры')),
            ],
            options={
                'verbose_name': ('Произведение',),
                'verbose_name_plural': 'Произведения',
                'ordering': ('-id',),
            },
        ),
    ]
