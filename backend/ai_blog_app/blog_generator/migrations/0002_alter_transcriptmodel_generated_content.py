# Generated by Django 4.2.4 on 2024-05-11 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_generator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcriptmodel',
            name='generated_content',
            field=models.CharField(max_length=1000),
        ),
    ]
