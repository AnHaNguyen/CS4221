# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-04 16:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ER2XML', '0005_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('colIds', models.CharField(max_length=10)),
                ('colNames', models.CharField(max_length=50)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keys', to='ER2XML.Table')),
            ],
        ),
        migrations.AlterField(
            model_name='column',
            name='tp',
            field=models.CharField(default=b'xs:string', max_length=10),
        ),
    ]