import settings


def websocket_address(request):
    return {'WEBSOCKET_ADDRESS': settings.get_websocket_address(request) }