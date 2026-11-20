import os
from typing import Any

from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageUploadRequestSerializer(serializers.Serializer):
	"""Тело запроса (multipart/form-data) — используется для схемы OpenAPI."""

	file = serializers.ImageField()


class ImageUploadResponseSerializer(serializers.Serializer):
	url = serializers.URLField()


class ImageUploadErrorSerializer(serializers.Serializer):
	error = serializers.CharField()


class ImageUploadView(APIView):
	permission_classes = [IsAdminUser]
	parser_classes = [MultiPartParser, FormParser]

	@extend_schema(
		request={"multipart/form-data": ImageUploadRequestSerializer},
		responses={
			200: ImageUploadResponseSerializer,
			400: ImageUploadErrorSerializer,
		},
		description=(
			"Загрузка изображения для контента статей (только для администраторов). "
			"Допустимые типы: JPEG, PNG, GIF, WebP."
		),
	)
	def post(
		self,
		request: Request,
		*args: Any,
		**kwargs: Any,
	) -> Response:
		uploaded_file = request.FILES.get("file")

		if not uploaded_file:
			return Response({"error": "No file provided"}, status=400)

		allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}

		if uploaded_file.content_type not in allowed:
			return Response({"error": "Unsupported file type"}, status=400)

		ext = os.path.splitext(uploaded_file.name or "")[1]
		filename = f"articles/content/{get_random_string(16)}{ext}"

		path = default_storage.save(filename, uploaded_file)
		url = request.build_absolute_uri(default_storage.url(path))

		return Response({"url": url})
