from rest_framework import serializers

from .models import WatchlistItem


class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = "__all__"


class UpdateStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    watched = serializers.BooleanField()
    notes = serializers.CharField()
