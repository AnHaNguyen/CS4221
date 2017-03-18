# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 00:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('tp', models.CharField(choices=[(b'xs:string', b'STRING'), (b'xs:integer', b'NUMERIC'), (b'xs:date', b'DATE'), (b'xs:boolean', b'BOOLEAN'), (b'xs:decimal', b'DECIMAL'), (b'xs:short', b'SHORT')], default=b'xs:string', max_length=10)),
                ('minOccur', models.IntegerField(null=True)),
                ('maxOccur', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Constraint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('constraintType', models.CharField(choices=[(b'NN', b'NOT_NULL'), (b'UNI', b'UNIQUE'), (b'PK', b'PRIMARY_KEY'), (b'FK', b'FOREIGN_KEY')], default=b'NN', max_length=3)),
                ('column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ER2XML.Column')),
            ],
        ),
        migrations.CreateModel(
            name='ERModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='ER2XML.ERModel')),
            ],
        ),
        migrations.CreateModel(
            name='XMLSchema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(null=True)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ER2XML.ERModel')),
            ],
        ),
        migrations.AddField(
            model_name='constraint',
            name='table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constraints', to='ER2XML.Table'),
        ),
        migrations.AddField(
            model_name='column',
            name='table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='columns', to='ER2XML.Table'),
        ),
    ]