from .models import User
class UserValidation:
    @staticmethod
    def userExist(user):
        query = User.objects.filter(email=user['email'])
        return query.exists()

        
