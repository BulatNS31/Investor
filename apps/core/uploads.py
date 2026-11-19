import os

from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=400)

        # простая валидация типа
        allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if file.content_type not in allowed:
            return Response({"error": "Unsupported file type"}, status=400)

        ext = os.path.splitext(file.name)[1]
        filename = f"articles/content/{get_random_string(16)}{ext}"
        path = default_storage.save(filename, file)
        url = request.build_absolute_uri(default_storage.url(path))

        return Response({"url": url})
