# -*- coding: utf-8 -*-

import django.contrib.auth.models as _djauthmods

import rest_framework.viewsets    as _drfview
import rest_framework.permissions as _dfrperm

from . import serializers


class UserViewSet(_drfview.ModelViewSet):
	queryset = _djauthmods.User.objects.order_by('username', 'date_joined')
	serializer_class   = serializers.UserSerializer
	permission_classes = [_dfrperm.IsAuthenticated]


class GroupViewSet(_drfview.ModelViewSet):
	queryset = _djauthmods.Group.objects.all()
	serializer_class   = serializers.GroupSerializer
	permission_classes = [_dfrperm.IsAuthenticated]
