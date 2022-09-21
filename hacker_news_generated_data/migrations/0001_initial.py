# Generated by Django 4.1.1 on 2022-09-13 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=200, null=True)),
                ('type', models.CharField(max_length=40, null=True)),
                ('by', models.CharField(blank=True, max_length=200, null=True)),
                ('time', models.DateField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('dead', models.BooleanField(blank=True, default=False, null=True)),
                ('parent', models.IntegerField(blank=True, null=True, unique=True)),
                ('poll', models.IntegerField(blank=True, null=True, unique=True)),
                ('url', models.URLField(blank=True, null=True, unique=True)),
                ('score', models.IntegerField(blank=True, null=True)),
                ('descendants', models.IntegerField(blank=True, null=True)),
                ('kids', models.TextField(blank=True, null=True)),
                ('parts', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='relations',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=200, null=True)),
                ('type', models.CharField(blank=True, max_length=40, null=True)),
                ('by', models.CharField(blank=True, max_length=200, null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, null=True, unique=True)),
                ('descendants', models.IntegerField(blank=True, null=True)),
                ('kids', models.TextField(blank=True, null=True)),
                ('parts', models.TextField(blank=True, null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hacker_news_generated_data.news')),
            ],
        ),
    ]
