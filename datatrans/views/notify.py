import structlog
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..gateway import handle_notification

logger = structlog.get_logger()


@require_POST
@csrf_exempt
def notify_handler(request: HttpRequest) -> HttpResponse:
    logger.info('datatrans-notification', body=request.body)
    handle_notification(request.body)
    return HttpResponse()  # If we were able to digest the notification (be it a success or an error), we are ok.
