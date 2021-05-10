# -*- coding: utf-8 -*-

import funcy as F
import urllib.parse

from django.urls import path, include, get_script_prefix
from django.utils.encoding import iri_to_uri

import rest_framework.routers     as _drfrout
import rest_framework.urlpatterns as _drfurl
import rest_framework.reverse     as _drfrev

from ..views import UserViewSet
from .views  import PollingViewSet, TextAnswerViewSet, ChoiceAnswerViewSet
from .views  import QuestionViewSet, ChoiceViewSet, QuestionAnswerViewSet
from .views  import question_redirect, choice_redirect

from .. import permissions


class APIRootView(_drfrout.APIRootView):
	permission_classes = [permissions.ReadOnly]

	def get(self, request, *args, **kwargs):
		response = super().get(request, *args, **kwargs)
		rooturl = _drfrev.reverse('api-root', request=request)

		urljoin = F.partial(urllib.parse.urljoin, rooturl)

		response.data['pollings[pk].questions']     = urljoin('pollings/{polling_pk}/questions/')
		response.data['pollings[pk].questions[pk]'] = urljoin('pollings/{polling_pk}/questions/{pk}/')
		response.data['questions[pk].choices']      = urljoin('questions/{question_pk}/choices/')
		response.data['questions[pk].choices[pk]']  = urljoin('questions/{question_pk}/choices/{pk}/')
		response.data['questions[pk].answers']      = urljoin('questions/{question_pk}/answers/')

		return response


router = _drfrout.DefaultRouter()
router.APIRootView = APIRootView

router.register('users',    UserViewSet)
router.register('pollings', PollingViewSet)
router.register('text_answers',   TextAnswerViewSet)
router.register('choice_answers', ChoiceAnswerViewSet)

list_polling_questions   = QuestionViewSet.as_view({'get': 'list', 'post': 'create'})
detail_polling_questions = QuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

list_question_choices   = ChoiceViewSet.as_view({'get': 'list', 'post': 'create'})
detail_question_choices = ChoiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

list_question_answers = QuestionAnswerViewSet.as_view({'get': 'list', 'post': 'create'})


urlpatterns = [
	path('', include(router.urls)),
] + _drfurl.format_suffix_patterns([

	path('questions/<int:pk>/', question_redirect, name='question-detail'),        # -> polling/<polling_pk>/questions/<pk>
	path('questions/<int:pk>/', question_redirect, name='choicequestion-detail'),  # -> polling/<polling_pk>/questions/<pk>
	path('choices/<int:pk>/',   choice_redirect,   name='choice-detail'),          # -> questions/<question_pk>/choices/<pk>

	path('pollings/<int:polling_pk>/questions/',          list_polling_questions,   name='polling-questions'),
	path('pollings/<int:polling_pk>/questions/<int:pk>/', detail_polling_questions, name='polling-questions'),
	path('questions/<int:question_pk>/choices/',          list_question_choices,    name='question-choices'),
	path('questions/<int:question_pk>/choices/<int:pk>/', detail_question_choices,  name='question-choices'),
	path('questions/<int:question_pk>/answers/',          list_question_answers,    name='question-answers'),
])
