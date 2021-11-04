def show_toolbar_callback(request):
    return request.GET.get('debug', None) == "y"
