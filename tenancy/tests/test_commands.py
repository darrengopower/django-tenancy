from __future__ import unicode_literals

from StringIO import StringIO

from django.db import connections
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test.testcases import TransactionTestCase

from ..models import Tenant, TenantModelBase

from .utils import mock_inputs, setup_custom_tenant_user, skipIfCustomTenant


@skipIfCustomTenant
class CreateTenantCommandTest(TransactionTestCase):
    def test_too_many_fields(self):
        args = ('name', 'useless')
        expected_message = (
            "Number of args exceeds the number of fields for model tenancy.Tenant.\n"
            "Got %s when defined fields are ('name',)." % repr(args)
        )
        with self.assertRaisesMessage(CommandError, expected_message):
            call_command('createtenant', *args)

    def test_full_clean_failure(self):
        expected_message = (
            'Invalid value for field "name": This field cannot be blank.'
        )
        with self.assertRaisesMessage(CommandError, expected_message):
            call_command('createtenant')

    def test_success(self):
        call_command('createtenant', 'tenant', verbosity=0)
        Tenant.objects.get(name='tenant').delete()

    def test_verbosity(self):
        stdout = StringIO()
        call_command('createtenant', 'tenant', stdout=stdout, verbosity=3)
        tenant = Tenant.objects.get(name='tenant')
        stdout.seek(0)
        connection = connections[tenant._state.db]
        if connection.vendor == 'postgresql':
            self.assertIn(tenant.db_schema, stdout.readline())
        for model in TenantModelBase.references:
            self.assertIn(model._meta.object_name, stdout.readline())
            self.assertIn(model._meta.db_table, stdout.readline())
        self.assertIn('Installing indexes ...', stdout.readline())
        tenant.delete()

    @setup_custom_tenant_user
    @mock_inputs((
        ('\nYou just created a new tenant,', 'yes'),
        ('Email', 'bleh@teant.test.ca'),
        ('Password', '1234')
    ))
    def test_superuser_creation_prompt(self):
        stdout = StringIO()
        call_command('createtenant', 'tenant', stdout=stdout, interactive=True)
        stdout.seek(0)
        self.assertIn('Superuser created successfully.', stdout.read())
        Tenant.objects.get(name='tenant').delete()
