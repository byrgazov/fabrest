# -*- coding: utf-8 -*-

import funcy     as F
import itertools as I

import logging

import django.contrib.auth.models as _djauthmods
import django.core.exceptions     as _djexc
import django.http                as _djhttp
import django.shortcuts           as _djshort
import django.utils.timezone      as _djtz

import rest_framework.decorators  as _drfdecor
import rest_framework.exceptions  as _drfexcs
import rest_framework.relations   as _drfrels
import rest_framework.serializers as _drfsers
import rest_framework.settings    as _drfsett

from . import models


logger = logging.getLogger('fabrest')


class PollingSerializer(_drfsers.HyperlinkedModelSerializer):
	created_by = _drfsers.CharField(source='created_by.username', required=False)
	updated_by = _drfsers.CharField(source='updated_by.username', allow_null=True, required=False)
	questions  = _drfsers.HyperlinkedIdentityField(view_name='polling-questions', lookup_url_kwarg='polling_pk')

	class Meta:
		model  = models.Polling
		fields = ['id', 'title', 'description', 'created_by', 'updated_by', 'start_time', 'duration', 'questions']

	# @xxx: (!) вся валидация с моделях у меня лежит в `clean` и из коробки здесь работать не будет
	#       DRF не делает `clean`

	def validate_created_by(self, value):
		for user in _djauthmods.User.objects.filter(username=value):
			return user
		raise _drfexcs.ValidationError('User "{}" doesn\'t exist.'.format(value))

	def validate_updated_by(self, value):
		return self.validate_created_by(value)

	def create(self, data):
		# @xxx: [bw] для валидации (clean)

		created_by = data.get('created_by')
		updated_by = data.get('updated_by')

		polling = self.Meta.model(**data)
		polling.full_clean()  # [bw] !!!
		polling.save()

		return polling

	def update(self, polling, data):
		# @xxx: [bw] для валидации (clean)

		for key, value in data.items():
			setattr(polling, key, value)

		polling.full_clean()  # [bw] !!!
		polling.save()

		return polling

#methods=['post'], detail=True, permission_classes=[IsAdminOrIsSelf], url_path='change-password', url_name='change_password'
#	@_drfdecor.action(methods=['get'], detail=True, url_path='questions', url_name='questions')
#	def get_questions(self, request, pk):
#		pass


class QuestionSerializer(_drfsers.Serializer):
	id      = _drfsers.IntegerField(min_value=1, read_only=True)
#	polling = _drfsers.ModelField(model_field=models.Question._meta.get_field('polling'))
	order   = _drfsers.IntegerField(min_value=1, required=False)
	description = _drfsers.CharField()

	has_choices = _drfsers.BooleanField(default=False, required=False)
	multiple    = _drfsers.BooleanField(default=True,  required=False)
	choices     = _drfsers.HyperlinkedIdentityField(view_name='question-choices', lookup_url_kwarg='question_pk', required=False)

	def to_representation(self, question):
		data = super().to_representation(question)
		if isinstance(question, models.TextQuestion):
			data.pop('has_choices', None)
			data.pop('multiple',    None)
			data.pop('choices',     None)
		if isinstance(question, models.ChoiceQuestion):
			data['has_choices'] = True
		return data

	def to_internal_value(self, data):
		data = super().to_internal_value(data)

		polling_pk = self.context['request'].resolver_match.kwargs['polling_pk']
		for polling in models.Polling.objects.filter(pk=polling_pk):
			break
		else:
			raise _drfexcs.ValidationError({
				_drfsett.api_settings.NON_FIELD_ERRORS_KEY: ['Polling #{} doesn\'t exist.'.format(polling_pk)]
			})

		data['polling'] = polling

		return data

#	def validate_polling(self, value):
#		for polling in models.Polling.objects.filter(pk=value):
#			return polling
#		raise _drfexcs.ValidationError('Polling #{} doesn\'t exist.'.format(value))

	def create(self, data):
		# @xxx: для веб-морды, всегда (!) data['multiple'] == True
		#       выглядит как косяк DRF

		if data.pop('has_choices', None):
			question = models.ChoiceQuestion(**data)
		else:
			data.pop('multiple', None)
			question = models.TextQuestion(**data)

		question.full_clean()
		question.save(force_insert=True)

		return question

	def update(self, question, data):
		# @xxx: для веб-морды, всегда (!) data['multiple'] == True
		#       выглядит как косяк DRF

		data.pop('has_choices', None)

		if isinstance(question, models.TextQuestion):
			data.pop('multiple', None)

		if 'polling' in data:
			data['polling'] = models.Polling.objects.get(pk=data['polling'])

		for key, value in data.items():
			setattr(question, key, value)

		question.full_clean()
		question.save()

		return question


class ChoiceOptionSerializer(_drfsers.HyperlinkedModelSerializer):
	class Meta:
		model  = models.ChoiceOption
		fields = ['id', 'question', 'text']


class TextAnswerSerializer(_drfsers.HyperlinkedModelSerializer):
	question = _drfsers.ModelField(model_field=models.TextAnswer._meta.get_field('question'))

	class Meta:
		model  = models.TextAnswer
		fields = ['guest_id', 'question', 'text']


class ChoiceAnswerSerializer(_drfsers.HyperlinkedModelSerializer):
	question = _drfsers.ModelField(model_field=models.ChoiceAnswer._meta.get_field('question'))

	class Meta:
		model  = models.ChoiceAnswer
		fields = ['guest_id', 'question', 'choice']


class ManyRelatedField(_drfsers.ManyRelatedField):
	# @xxx: зто Django, детка

	def get_attribute(self, instance):
		try:
			return super().get_attribute(instance)
		except (KeyError, AttributeError):
			return self.get_default()


class ChoicesField(_drfsers.HyperlinkedIdentityField):
	# @xxx: зто Django, детка

	default_error_messages = dict(_drfsers.HyperlinkedIdentityField.default_error_messages, **{
		'does_not_exist'  : 'Object does not exist.',
		'internal_error'  : 'Internal error.',
		'invalid_question': 'Question has no choices.',
	})

	def __new__(cls, **kwargs):
		if kwargs:
			return super().__new__(cls, **kwargs)
		return cls.many_init(view_name='choice-detail', default=None, required=False)

	@classmethod
	def many_init(cls, *args, **kwargs):
		list_kwargs = {'child_relation': cls(*args, **kwargs)}
		for key in kwargs:
			if key in _drfrels.MANY_RELATION_KWARGS:
				list_kwargs[key] = kwargs[key]
		return ManyRelatedField(**list_kwargs)

	@property
	def read_only(self):
		return False

	@read_only.setter
	def read_only(self, value):
		pass

	def get_queryset(self):
		question = self.root.get_question()
		return models.ChoiceOption.objects.filter(question_id=question.pk)

	def get_object(self, view_name, view_args, view_kwargs):
		question = self.root.get_question()

		if not isinstance(question, models.ChoiceQuestion):
			self.fail('invalid_question')

		lookup_kwargs = {
			self.lookup_field: view_kwargs[self.lookup_url_kwarg],
			'question_id'    : question.pk,
		}

		queryset = self.get_queryset()

		try:
			return queryset.get(**lookup_kwargs)
		except _djexc.ObjectDoesNotExist:
			self.fail('does_not_exist')
		except Exception:
			logger.exception('Unhandled error')  # @ex: _djexc.MultipleObjectsReturned
			self.fail('internal_error')

	def to_internal_value(self, data):
		if type(data) is int or type(data) is str and data.isdigit():
			return self.get_object(self.view_name, (), {'pk': int(data)})
		return super().to_internal_value(data)


class QuestionAnswerSerializer(_drfsers.Serializer):
	guest_id = _drfsers.IntegerField(min_value=1)
	text     = _drfsers.CharField(default=None, required=False)
	choices  = ChoicesField()

	default_error_messages = dict(_drfsers.Serializer.default_error_messages, **{
		'required_field'  : 'This field is required.',
		'invalid_question': 'Question does not exist or has no choices.',
		'just_one_option' : 'Question has just one option.',
		'unknown_question': 'Unknown question kind: {question!r}',
		'unknown_fields'  : 'Unknown fields: {fields}',
		'internal_error'  : 'Internal error.',
		'polling_not_started': 'Polling has not started yet.',
		'polling_ended'      : 'Polling has already ended.',
	})

	def fail(self, key, **kwargs):
		# @xxx: Django-стайл-прон-фикс
		field = kwargs.pop('__field__', None)
		try:
			super().fail(key, **kwargs)
		except _drfexcs.ValidationError as exc:
			if field is not False and isinstance(exc.detail, (list, tuple)) and len(exc.detail) == 1:
				exc = _drfexcs.ValidationError({field or _drfsett.api_settings.NON_FIELD_ERRORS_KEY: exc.detail})
			raise exc.with_traceback(exc.__traceback__)

	def get_question(self):
		if 'question' in self.context:
			return self.context['question']

		question_pk = self.context['request'].resolver_match.kwargs['question_pk']

		questions = I.chain(
			models.TextQuestion.objects.filter(pk=question_pk),
			models.ChoiceQuestion.objects.filter(pk=question_pk))

		question = F.first(questions)

		if question is None:
			self.fail('invalid_question')  # @xxx: (!) иногда нужно __field__=False -> сделать что-нибудь с `fail`

		self.context['question'] = question

		return question

	def validate_text(self, text):
		question = self.get_question()
		if isinstance(question, models.TextQuestion) and not text:
			self.fail('required_field', __field__=False)
		return text

	def validate_choices(self, choices):
		question = self.get_question()
		if isinstance(question, models.ChoiceQuestion):
			choices = choices or []
			if not question.multiple and 1 < len(choices):
				self.fail('just_one_option', __field__=False)
			if not question.multiple and not choices:
				self.fail('required_field', __field__=False)
		return choices

	def to_representation(self, answer):
		data = super().to_representation(answer)
		if isinstance(answer, models.TextAnswer):
			data.pop('choices', None)
		if isinstance(answer, models.ChoiceAnswer):
			data.pop('text', None)
		return data

	def to_internal_value(self, data):
		question = self.get_question()
		polling  = question.polling

		now = _djtz.localtime(timezone=_djtz.get_default_timezone())

		if now < polling.start_time:
			self.fail('polling_not_started')

		if polling.start_time + polling.duration <= now:
			self.fail('polling_ended')

		data = super().to_internal_value(data)
		data['question'] = question

		data = F.select_values(F.complement(F.isnone), data)

		logger.debug('QuestionAnswerSerializer.to_internal_value(%r)', data)

		if isinstance(question, models.TextQuestion):
			kwargs = F.project(data, 'guest_id question text'.split())
			rest   = F.project(data, F.without(data, *kwargs.keys()))
		elif isinstance(question, models.ChoiceQuestion):
			kwargs = F.project(data, 'guest_id question choices'.split())
			rest   = F.project(data, F.without(data, *kwargs.keys()))
		else:
			self.fail('unknown_question', question=question)

		if rest:
			self.fail('unknown_fields', fields=dict(rest))

		return data

	def create(self, data):
		logger.debug('QuestionAnswerSerializer.create(%r)', data)

		question = data['question']

		if isinstance(question, models.TextQuestion):
			answer = models.TextAnswer(**data)

		if isinstance(question, models.ChoiceQuestion):
			choices = data.pop('choices', [])
			answer  = models.ChoiceAnswer(**data)

		try:
			answer.full_clean()
			answer.save(force_insert=True)
		except _djexc.ValidationError as exc:
			# @xxx: {'__all__': [...]} -> {'non_field_errors': [...]}
			raise _drfexcs.ValidationError(detail=_drfsers.as_serializer_error(exc))

		if isinstance(question, models.ChoiceQuestion) and choices:
			try:
				# @todo: transaction
				answer.choices.set(choices)
				answer.save()
			except Exception:
				answer.delete()
				logger.exception('Unhandled error')
				self.fail('internal_error')
			except:
				answer.delete()
				raise

		return answer
