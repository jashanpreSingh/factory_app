from rest_framework import serializers


class AssistantMessageSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000, trim_whitespace=True)
    page = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
