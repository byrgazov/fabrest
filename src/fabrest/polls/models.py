# -*- coding: utf-8 -*-

import datetime

import django.contrib.auth        as _djauth
import django.contrib.auth.models as _djauthmodels
import django.core.exceptions     as _djexc
import django.db.models           as _djmodels
import django.utils.timezone      as _djtz

import dirtyfields
import django_currentuser.db.models as _djcurmodels


def get_sentinel_user():
	return _djauth.get_user_model().objects\
		.get_or_create(username='.deleted')[0]


class Polling(dirtyfields.DirtyFieldsMixin, _djmodels.Model):
	title       = _djmodels.CharField(max_length=200, unique=True)
	description = _djmodels.TextField()
	created_by  = _djcurmodels.CurrentUserField(related_name='questions_created', on_delete=_djmodels.SET(get_sentinel_user))
	updated_by  = _djcurmodels.CurrentUserField(related_name='questions_updated', on_delete=_djmodels.SET(get_sentinel_user), on_update=True)
	start_time  = _djmodels.DateTimeField()
	duration    = _djmodels.DurationField()

	class Meta:
		ordering = ['start_time', 'title']

	def __repr__(self):
		return '<Polling #{} "{}">'.format(self.id or '?', self.title or '')

	def clean(self):
		if self.duration is not None and self.duration <= datetime.timedelta(0):
			raise _djexc.ValidationError({'duration': 'Duration cannot be negative'})

		prev_start_time = self.get_dirty_fields().get('start_time')

		if self.start_time and prev_start_time and self.start_time != prev_start_time:
			now = _djtz.localtime(timezone=_djtz.get_default_timezone())
			if prev_start_time <= now:
				raise _djexc.ValidationError({'start_time': 'Start time can\'t be modified, too late'})


class Question(_djmodels.Model):
	polling     = _djmodels.ForeignKey(Polling, related_name='questions', on_delete=_djmodels.CASCADE)
	order       = _djmodels.PositiveIntegerField(default=0)
	description = _djmodels.TextField()

	def clean_fields(self, exclude=None):
		if not exclude or 'order' not in exclude:
			if not self.order and self.polling:
				try:
					last_order = self.polling.questions.latest('order').order
					self.order = round((last_order + 9) / 10) * 10
				except _djmodels.ObjectDoesNotExist:
					self.order = 10
		return super().clean_fields(exclude=exclude)


class TextQuestion(Question):
	pass


class ChoiceQuestion(Question):
	multiple = _djmodels.BooleanField('Multiple choice', default=True)


class ChoiceOption(_djmodels.Model):
	question = _djmodels.ForeignKey(ChoiceQuestion, related_name='choices', on_delete=_djmodels.CASCADE)
	text     = _djmodels.CharField(max_length=200)

	class Meta:
		unique_together = ['question', 'text']


class TextAnswer(_djmodels.Model):
	guest_id = _djmodels.PositiveIntegerField()
	question = _djmodels.ForeignKey(TextQuestion, related_name='text_answers', on_delete=_djmodels.CASCADE)
	text     = _djmodels.TextField()

	class Meta:
		unique_together = ['guest_id', 'question']


class ChoiceAnswer(_djmodels.Model):
	guest_id = _djmodels.PositiveIntegerField()
	question = _djmodels.ForeignKey(ChoiceQuestion,    related_name='choice_answers', on_delete=_djmodels.CASCADE)
	choices  = _djmodels.ManyToManyField(ChoiceOption, related_name='answers')

	class Meta:
		unique_together = ['guest_id', 'question']
