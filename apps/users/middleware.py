from django.utils.deprecation import MiddlewareMixin
from apps.address.models import StoreLocations
from django.contrib.auth.models import AnonymousUser
from threading import local

STORE_ATTR = "store"
_thread_locals = local()


def _do_set_current_store(store_fun):
    setattr(_thread_locals, STORE_ATTR, store_fun.__get__(store_fun, local))


def _set_current_user(user=None):
    '''
    Sets current user in local thread.

    Can be used as a hook e.g. for shell jobs (when request object is not
    available).
    '''
    _do_set_current_user(lambda self: user)


class StaffManagerMiddleWare(MiddlewareMixin):


    def process_request(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        store_id = request.META.get('HTTP_STOREID', '')
        if store_id and store_id.isnumeric():
            request.store_profile = StoreLocations.objects.get(id=store_id)
            _do_set_current_store(lambda self: getattr(request, 'store_profile', None))


        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


def get_current_store():
    current_user = getattr(_thread_locals, STORE_ATTR, None)
    if callable(current_user):
        return current_user()
    return current_user

def get_current_authenticated_store():
    current_user = get_current_store()
    if isinstance(current_user, AnonymousUser):
        return None
    return current_user
