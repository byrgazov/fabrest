# -*- coding: utf-8 -*-

import functools
import itertools as I
import operator  as O

import django.http      as _djhttp
import django.shortcuts as _djshort
import django.urls      as _djurl
#import django.views.generic as _djvgen

import rest_framework.mixins      as _drfmx
import rest_framework.permissions as _drfperm
import rest_framework.response    as _drfresp
import rest_framework.status      as _drfstatus
import rest_framework.viewsets    as _drfviewsets

from .. import permissions
from .  import models
from .  import serializers


def question_redirect(request, pk):
	# questions/<pk> -> polling/<polling_pk>/questions/<pk>
	question = _djshort.get_object_or_404(models.Question, pk=pk)
	url = _djurl.reverse('polling-questions', kwargs={'polling_pk': question.polling.id, 'pk': pk})
	return _djhttp.HttpResponseRedirect(url)


def choice_redirect(request, pk):
	# choices/<pk> -> questions/<question_pk>/choices/<pk>
	choice = _djshort.get_object_or_404(models.ChoiceOption, pk=pk)
	url = _djurl.reverse('question-choices', kwargs={'question_pk': choice.question.id, 'pk': pk})
	return _djhttp.HttpResponseRedirect(url)


class PollingViewSet(_drfviewsets.ModelViewSet):
	queryset         = models.Polling.objects.all()
	serializer_class = serializers.PollingSerializer
	permission_classes = [_drfperm.IsAdminUser | permissions.ReadOnly]


class CRUDMixin(_drfmx.CreateModelMixin, _drfmx.UpdateModelMixin, _drfmx.RetrieveModelMixin, _drfmx.DestroyModelMixin):
	pass


class QuestionViewSet(CRUDMixin, _drfviewsets.ViewSet):
	# @ex: pollings/<int:polling_pk>/questions/          -- List, Create
	# @ex: pollings/<int:polling_pk>/questions/<int:pk>/ -- Get, Update, Delete

	serializer_class   = serializers.QuestionSerializer
	permission_classes = [_drfperm.IsAdminUser | permissions.ReadOnly]

	def get_object(self):
		polling_pk  = self.kwargs['polling_pk']
		question_pk = self.kwargs.get('pk')

		if question_pk is None:
			polling = _djshort.get_object_or_404(models.Polling, pk=polling_pk)

			ids = functools.reduce(O.add, polling.questions.values_list('id'), ())

			questions = I.chain(
				models.TextQuestion.objects.filter(pk__in=ids),
				models.ChoiceQuestion.objects.filter(pk__in=ids))

			questions = sorted(questions, key=O.attrgetter('order'))

			for no, question in list(enumerate(questions))[::-1]:
				for permission in self.get_permissions():
					if not permission.has_object_permission(self.request, self, question):
						del questions[no]

			return questions  # @xxx: <list>

		questions = I.chain(
			models.TextQuestion.objects.filter(polling_id=polling_pk, pk=question_pk),
			models.ChoiceQuestion.objects.filter(polling_id=polling_pk, pk=question_pk))

		for question in questions:
			self.check_object_permissions(self.request, question)
			return question

		raise _djhttp.Http404

	def get_serializer(self, *args, **kwargs):
		ctx = kwargs.setdefault('context', {})
		ctx.setdefault('request', self.request)
		ctx.setdefault('format',  self.format_kwarg)
		ctx.setdefault('view',    self)
		return self.serializer_class(*args, **kwargs)

	def list(self, request, polling_pk):
		questions  = self.get_object()
		serializer = self.get_serializer(questions, many=True)
		return _drfresp.Response(serializer.data)


class ChoiceViewSet(CRUDMixin, _drfviewsets.ViewSet):
	# @ex: questions/<int:question_pk>/choices/          -- List, Create
	# @ex: questions/<int:question_pk>/choices/<int:pk>/ -- Get, Update, Delete

	serializer_class   = serializers.ChoiceOptionSerializer
	permission_classes = [_drfperm.IsAdminUser | permissions.ReadOnly]

	def get_queryset(self):
		if self.kwargs.get('pk') is None:
			return models.ChoiceQuestion.objects.filter(pk=-1)
		return models.ChoiceOption.objects.filter(pk=-1)

	def get_object(self):
		qpk = self.kwargs['question_pk']
		cpk = self.kwargs.get('pk')

		if cpk is None:
			obj = _djshort.get_object_or_404(models.ChoiceQuestion, pk=qpk)
		else:
			obj = _djshort.get_object_or_404(models.ChoiceOption, question_id=qpk, pk=cpk)

		self.check_object_permissions(self.request, obj)

		return obj

	def get_serializer(self, *args, **kwargs):
		ctx = kwargs.setdefault('context', {})
		ctx.setdefault('request', self.request)
		ctx.setdefault('format',  self.format_kwarg)
		ctx.setdefault('view',    self)
		return self.serializer_class(*args, **kwargs)

	def list(self, request, question_pk):
		question   = self.get_object()
		serializer = self.get_serializer(question.choices, many=True)
		return _drfresp.Response(serializer.data)


class TextAnswerViewSet(_drfviewsets.ModelViewSet):
	queryset         = models.TextAnswer.objects.all()
	serializer_class = serializers.TextAnswerSerializer
	permission_classes = [_drfperm.IsAdminUser]


class ChoiceAnswerViewSet(_drfviewsets.ModelViewSet):
	queryset         = models.ChoiceAnswer.objects.all()
	serializer_class = serializers.ChoiceAnswerSerializer
	permission_classes = [_drfperm.IsAdminUser]


class QuestionAnswerViewSet(_drfmx.CreateModelMixin, _drfviewsets.ViewSet):
	# @ex: questions/<int:question_pk>/answers/ -- List, Create

	serializer_class   = serializers.QuestionAnswerSerializer
	permission_classes = [_drfperm.AllowAny]

	def get_queryset(self):
		question_pk = self.kwargs['question_pk']

		for question in models.TextQuestion.objects.filter(pk=question_pk):
			return models.TextAnswer.objects.filter(question_id=question_pk)

		return models.ChoiceAnswer.objects.filter(question_id=question_pk)

	def get_object(self):
		question_pk = self.kwargs['question_pk']

		answers = I.chain(
			models.TextAnswer.objects.filter(question_id=question_pk),
			models.ChoiceAnswer.objects.filter(question_id=question_pk))

		answers = sorted(answers, key=lambda answer: (answer.guest_id, answer.id))

		for no, answer in list(enumerate(answers))[::-1]:
			for permission in self.get_permissions():
				if not permission.has_object_permission(self.request, self, answer):
					del answers[no]

		return answers  # @xxx: <list>

	def get_serializer(self, *args, **kwargs):
		ctx = kwargs.setdefault('context', {})
		ctx.setdefault('request', self.request)
		ctx.setdefault('format',  self.format_kwarg)
		ctx.setdefault('view',    self)
		return self.serializer_class(*args, **kwargs)

	def list(self, request, question_pk):
		answers    = self.get_object()
		serializer = self.get_serializer(answers, many=True)
		return _drfresp.Response(serializer.data)
