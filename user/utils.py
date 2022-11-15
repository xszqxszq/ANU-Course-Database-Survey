from user.models import User
import hashlib

def getAuth(user):
	return hashlib.md5((user.password + str(user.userId) + user.username).encode('UTF-8')).hexdigest()

def getUser(request):
	username = request.COOKIES.get('username')
	auth = request.COOKIES.get('auth')
	if username and auth:
		user = User.objects.filter(username=username).first()
		if user and auth == getAuth(user):
			return user
		else:
			return None
	return None