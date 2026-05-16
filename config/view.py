import io
import threading

from django.conf import settings
from django.core.management import call_command
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView
from rest_framework.response import Response        


_er_refresh_lock = threading.Lock()


class RootApiView(APIView):
    def get(self, request):
        return Response({
            "message": "Welcome to the Accounts API",
            "endpoints": {
                "login": "/login/",
                "change_password": "/change-password/",
                "token_refresh": "/token/refresh/",
                "me": "/me/",
                "departments": "/departments/",
            }
        })


def _dev_er_response(payload, status=200):
    response = JsonResponse(payload, status=status)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Accept, Content-Type"
    return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def refresh_er_explorer(request):
    if request.method == "OPTIONS":
        return _dev_er_response({"ok": True})

    if not (settings.DEBUG or getattr(settings, "ER_EXPLORER_REFRESH_ENABLED", False)):
        return _dev_er_response(
            {
                "ok": False,
                "error": (
                    "ER explorer refresh is disabled. Set DEBUG=True or "
                    "ER_EXPLORER_REFRESH_ENABLED=true for local use."
                ),
            },
            status=404,
        )

    if not _er_refresh_lock.acquire(blocking=False):
        return _dev_er_response(
            {"ok": False, "error": "An ER explorer refresh is already running."},
            status=409,
        )

    output = io.StringIO()
    try:
        call_command("refresh_er_explorer", stdout=output)
    except Exception as exc:
        return _dev_er_response(
            {"ok": False, "error": str(exc), "output": output.getvalue()},
            status=500,
        )
    finally:
        _er_refresh_lock.release()

    return _dev_er_response(
        {
            "ok": True,
            "generatedAt": timezone.localtime().isoformat(timespec="seconds"),
            "output": output.getvalue(),
        }
    )
