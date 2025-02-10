from adrf.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from .models import Job

__all__ = [
    "JobSerializer",
    "CoordinateSerializer",
    "LineSerializer",
    "PageSerializer",
    "DocumentSerializer",
]


class JobSerializer(ModelSerializer):
    result = serializers.JSONField()

    class Meta:
        model = Job
        fields = ["id", "multi_doc", "status", "result", "created_at", "updated_at"]
        read_only_fields = ["id", "multi_doc", "status", "result", "created_at", "updated_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.status == "completed":
            # Multiple documents case
            representation["result"] = {
                "documents": [DocumentSerializer(doc).data for doc in instance.result["documents"]],
                "message": instance.result["message"],
            }

        return representation


class PathSerializer(Serializer):
    path = serializers.CharField()
    single_file = serializers.BooleanField(default=True)


class MultipartSerializer(Serializer):
    file = serializers.FileField()
    single_file = serializers.BooleanField(default=True)

    def validate_file(self, value):
        valid_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".zip"]
        ext = value.name.split(".")[-1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}")


class CoordinateSerializer(Serializer):
    """Serializer for (x,y) coordinate pairs"""

    x = serializers.IntegerField()
    y = serializers.IntegerField()


class LineSerializer(Serializer):
    """Serializer for a line of text with its bounding box coordinates"""

    text = serializers.CharField()
    bbox = CoordinateSerializer(many=True)  # List of coordinate pairs

    def to_representation(self, instance):
        # If bbox is a list of tuples, convert to list of lists
        if isinstance(instance, dict):
            bbox = instance["bbox"]
        else:
            bbox = instance.bbox

        return {
            "text": instance.text if hasattr(instance, "text") else instance["text"],
            "bbox": [[coord[0], coord[1]] for coord in bbox],
        }


class PageSerializer(Serializer):
    """Serializer for a page containing lines and full text"""

    page_number = serializers.IntegerField()
    lines = LineSerializer(many=True)
    text = serializers.CharField()


class DocumentSerializer(serializers.Serializer):
    """Serializer for the complete document"""

    file_path = serializers.CharField()
    pages = PageSerializer(many=True)
