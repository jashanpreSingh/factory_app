from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.permissions import HasCompanyContext

from .serializers import AssistantMessageSerializer
from .services import (
    AssistantConfigError,
    AssistantProviderError,
    FactoryAssistantService,
)


class AssistantChatAPI(APIView):
    """Read-only Factory AI assistant."""

    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request):
        serializer = AssistantMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = FactoryAssistantService(
            company=request.company.company,
            company_code=request.company.company.code,
            user=request.user,
        )
        try:
            result = service.answer(
                question=serializer.validated_data['question'],
                page=serializer.validated_data.get('page', ''),
            )
        except AssistantConfigError as exc:
            return Response(
                {'error': str(exc), 'code': 'ai_not_configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AssistantProviderError as exc:
            return Response(
                {'error': str(exc), 'code': 'ai_provider_error'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result)
