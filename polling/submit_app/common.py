




def get_client_ip(request):
    ip=""
    csrf = request.META.get('CSRF_COOKIE','')

    if len(csrf) < 1:
        return "NOT_A_VALID_REQUEST"

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    elif request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip+'|'+csrf
