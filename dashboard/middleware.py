from django.shortcuts import redirect

class AdminMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith('/bazarx-admin/'):
            if not request.path.startswith('/bazarx-admin/login/'):
                if not request.user.is_authenticated:
                    return redirect('/bazarx-admin/login/')
                elif not request.user.is_staff:
                    return redirect('/')

        response = self.get_response(request)
        return response