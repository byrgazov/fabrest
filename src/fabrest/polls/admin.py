# -*- coding: utf-8 -*-

import django.contrib.admin as _djadmin
import django.forms.models  as _djforms
import django.utils.html    as _djhtml

from .models import Polling, TextQuestion, ChoiceQuestion, ChoiceOption
from .models import TextAnswer, ChoiceAnswer


class PollingAdmin(_djadmin.ModelAdmin):
	list_display = ('field_start_time', 'title', 'created_by')

	def field_start_time(self, polling):
		return _djhtml.mark_safe(polling.start_time.strftime('%Y-%m-%d&nbsp;%H:%M&nbsp;%Z'))
	field_start_time.short_description = 'Start time'
	field_start_time.admin_order_field = 'start_time'


class ChoiceInline(_djadmin.StackedInline):
	model = ChoiceOption
	extra = 3


class TextQuestionAdmin(_djadmin.ModelAdmin):
	list_display = ('field_polling', 'order')

	def field_polling(self, question):
		return '{}. {}'.format(question.polling.id, question.polling.title)
	field_polling.short_description = 'Polling'
	field_polling.admin_order_field = 'polling'


class ChoiceQuestionAdmin(_djadmin.ModelAdmin):
	list_display = ('field_polling', 'order')
	inlines = [ChoiceInline]

	def field_polling(self, question):
		return '{}. {}'.format(question.polling.id, question.polling.title)
	field_polling.short_description = 'Polling'
	field_polling.admin_order_field = 'polling'


_djadmin.site.register(Polling, PollingAdmin)
_djadmin.site.register(TextQuestion, TextQuestionAdmin)
_djadmin.site.register(ChoiceQuestion, ChoiceQuestionAdmin)
_djadmin.site.register(ChoiceOption)
_djadmin.site.register(TextAnswer)
_djadmin.site.register(ChoiceAnswer)
# ...
