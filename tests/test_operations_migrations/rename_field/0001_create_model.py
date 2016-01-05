# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from tenancy.models import Managed
from tenancy.operations import AddFied, CreateModel


class Migration(migrations.Migration):

    operations = [
        CreateModel(
            name='RenameField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charfield', models.TextField())
            ],
            bases=(models.Model,),
            options={
                'managed': Managed('tenancy.Tenant'),
            }
        ),
        AddFied('RenameField', 'foreign_key', models.ForeignKey('self', on_delete=models.CASCADE, null=True)),
    ]
