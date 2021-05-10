# -*- coding: utf-8 -*-

import datetime

import django.core.exceptions as _djexc
import django.db              as _djdb
import django.utils.timezone  as _djtz
import django.test

from .models import get_sentinel_user, Polling


class PollingModelTests(django.test.TestCase):
	def test_few_null_fails(self):
		polling = Polling(title='title', description='text')
		with self.assertRaises(_djexc.ValidationError):
			polling.full_clean()
		with self.assertRaises(_djdb.IntegrityError) as ectx:
			polling.save()
		self.assertIn('NOT NULL', str(ectx.exception))

	def test_zero_duration(self):
		polling = Polling(title='title', description='text',
			created_by=get_sentinel_user(),
			start_time=_djtz.localtime(),
			duration  =datetime.timedelta(0))

		with self.assertRaises(_djexc.ValidationError) as ectx:
			polling.full_clean()
		self.assertEqual(['duration'], list(ectx.exception.message_dict))

		polling.save()

	def test_negative_duration(self):
		polling = Polling(title='title', description='text',
			created_by=get_sentinel_user(),
			start_time=_djtz.localtime(),
			duration  =datetime.timedelta(-12))

		with self.assertRaises(_djexc.ValidationError) as ectx:
			polling.full_clean()
		self.assertEqual(['duration'], list(ectx.exception.message_dict))

		polling.save()

	def test_modify_start_time_ok(self):
		polling = Polling(title='title', description='text',
			created_by=get_sentinel_user(),
			start_time=_djtz.localtime(
				datetime.datetime.now(_djtz.get_current_timezone()) + datetime.timedelta(hours=1),
				_djtz.get_current_timezone()),
			duration  =datetime.timedelta(1))

		polling.full_clean()
		polling.save()

		polling.start_time += datetime.timedelta(seconds=1)

		polling.full_clean()
		polling.save()

	def test_modify_start_time_fail(self):
		polling = Polling(title='title', description='text',
			created_by=get_sentinel_user(),
			start_time=_djtz.localtime(),
			duration  =datetime.timedelta(1))

		polling.full_clean()
		polling.save()

		polling.start_time += datetime.timedelta(seconds=1)

		with self.assertRaises(_djexc.ValidationError) as ectx:
			polling.full_clean()
		self.assertEqual(['start_time'], list(ectx.exception.message_dict))

		polling.save()
