from rest_framework import serializers

__all__ = [
    "RequestSerializer",
    "ErrorMesageSerializer",
    "JobResponseSerializer",
    "LineSerializer",
    "PageSerializer",
    "ResponseSerializer",
]


class RequestSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        # Validate file type
        if not (value.name.endswith(".pdf") or value.name.endswith(".png")):
            raise serializers.ValidationError("File must be a PDF or PNG.")
        return value


class ErrorMesageSerializer(serializers.Serializer):
    message = serializers.CharField()


class JobResponseSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    file_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    completed = serializers.BooleanField()


class LineSerializer(serializers.Serializer):
    line_number = serializers.IntegerField()
    text = serializers.CharField()
    bbox = serializers.ListField(child=serializers.IntegerField())


class PageSerializer(serializers.Serializer):
    page_number = serializers.IntegerField()
    text = serializers.CharField()
    lines = LineSerializer(many=True)


class ResponseSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    file_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    completed = serializers.BooleanField()
    pages = PageSerializer(many=True)
