from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def iclock_getrequest(request):
    serial = request.GET.get('SN')
    info = request.GET.get('INFO')

    logger.info(f"Device Connected: SN={serial}, INFO={info}")

    return HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?><GetRequest><Status>OK</Status></GetRequest>',
        content_type="application/xml"
    )


@csrf_exempt
def iclock_cdata(request):
    if request.method == 'POST':
        serial = request.GET.get('SN')
        table = request.GET.get('table')
        raw_data = request.body.decode('utf-8', errors='ignore')


        logger.info(f"ZKTeco POST: SN={serial}, Table={table}")
        logger.info(f"Raw:\n{raw_data}")

        if table == 'ATTLOG':
            from .utils import process_attendance_data
            process_attendance_data(raw_data, serial)

    return HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?><Response><Status>OK</Status></Response>',
        content_type="application/xml"
    )
