# Generated by Django 4.1.1 on 2022-09-18 17:23

from django.db import migrations, models
import django.db.models.deletion
import user_added_data.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_added_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPosts',
            fields=[
                ('title', models.CharField(max_length=200, null=True)),
                ('type', models.CharField(max_length=40, null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('dead', models.BooleanField(blank=True, default=False, null=True)),
                ('parent', models.IntegerField(blank=True, null=True, unique=True)),
                ('poll', models.IntegerField(blank=True, null=True, unique=True)),
                ('url', models.URLField(blank=True, null=True, unique=True)),
                ('score', models.IntegerField(blank=True, null=True)),
                ('descendants', models.IntegerField(blank=True, null=True)),
                ('kids', models.TextField(blank=True, null=True)),
                ('id', models.BigAutoField(default=user_added_data.models.createID, primary_key=True, serialize=False, unique=True)),
                ('by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_added_data.user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
