from django.utils.deprecation import MiddlewareMixin
class DatabaseRouter:
    def _default_db( self ):
        return 'default'

    def db_for_read( self, model, **hints ):
        return self._default_db() + '_read'

    def db_for_write( self, model, **hints ):
        return self._default_db()

    
    def allow_relation(self, obj1, obj2, **hints):
        # I couldn't understand what would do this method
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return db == self._default_db()

    
    class StaffManagerMiddleWare(MiddlewareMixin):


        def process_request(self, request):
            # Code to be executed for each request before
            # the view (and later middleware) are called.
            access_token = request.META.get('HTTP_STORE_ID', '')
            print(access_token)
            print('aaaaaaaaaaaaaaaaaa')

            response = self.get_response(request)

            # Code to be executed for each request/response after
            # the view is called.

            return None