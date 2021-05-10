# -*- coding: utf-8 -*-

import rest_framework.permissions as _drfperm


class ReadOnly(_drfperm.BasePermission):
	def has_permission(self, request, view):
		return request.method in _drfperm.SAFE_METHODS
