# Generated by Django 2.0.4 on 2018-05-10 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]