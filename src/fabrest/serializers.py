# -*- coding: utf-8 -*-

import django.contrib.auth.models as _djauthmods
import rest_framework.serializers as _drfsers


class UserSerializer(_drfsers.HyperlinkedModelSerializer):
	class Meta:
		model  = _djauthmods.User
		fields = ['username', 'groups', 'is_staff']


class GroupSerializer(_drfsers.HyperlinkedModelSerializer):
	class Meta:
		model  = _djauthmods.Group
		fields = ['name', 'users']
