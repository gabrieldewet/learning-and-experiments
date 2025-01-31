from adrf.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from .models import Job

__all__ = [
    "RequestSerializer",
    "JobResponseSerializer",
    "LineSerializer",
    "PageSerializer",
    "ResponseSerializer",
]


class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "status", "result", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "result", "created_at", "updated_at"]


class PathSerializer(Serializer):
    path = serializers.CharField()
    single_file = serializers.BooleanField(default=True)


class MultipartSerializer(Serializer):
    file = serializers.FileField()
    single_file = serializers.BooleanField(default=True)


class RequestSerializer(Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        # Validate file type
        if not (value.name.endswith(".pdf") or value.name.endswith(".png")):
            raise serializers.ValidationError("File must be a PDF or PNG.")
        return value


class JobResponseSerializer(Serializer):
    job_id = serializers.CharField()
    file_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    completed = serializers.BooleanField()


class LineSerializer(Serializer):
    line_number = serializers.IntegerField()
    text = serializers.CharField()
    bbox = serializers.ListField(child=serializers.IntegerField())


class PageSerializer(Serializer):
    page_number = serializers.IntegerField()
    text = serializers.CharField()
    lines = LineSerializer(many=True)


class ResponseSerializer(Serializer):
    job_id = serializers.CharField()
    file_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    completed = serializers.BooleanField()
    pages = PageSerializer(many=True)
