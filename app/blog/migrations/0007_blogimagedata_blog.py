# Generated by Django 3.2.13 on 2022-06-06 07:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_blog_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogimagedata',
            name='blog',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.blog'),
        ),
    ]
