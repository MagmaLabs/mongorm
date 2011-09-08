from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.core.exceptions import SuspiciousOperation
from django.utils.encoding import force_unicode

from mongorm import *
from mongorm.errors import OperationError

from datetime import datetime


class MongoSession(Document):
	sessionKey = StringField( primaryKey=True )
	sessionData = StringField()
	expireDate = DateTimeField()
	
	##meta = {'collection': 'django_session', 'allow_inheritance': False}


class SessionStore(SessionBase):
	"""A MongoEngine-based session store for Django.
	"""
	
	def __init__( self, session_key=None ):
		super(SessionStore, self).__init__( session_key )
	
	def load( self ):
		try:
			session = MongoSession.objects.get(
				sessionKey=self.session_key,
				expireDate__gt=datetime.now()
			)
			return self.decode( force_unicode( session.sessionData ) )
		except MongoSession.DoesNotExist:
			self.create( )
			return {}

	def create( self ):
		while True:
			self.session_key = self._get_new_session_key()
			try:
				self.save( mustCreate=True )
			except CreateError:
				continue
			self.modified = True
			self._session_cache = {}
			return

	def exists(self, session_key):
		return MongoSession.objects.filter(
			sessionKey=session_key,
			expireDate__gt=datetime.now()
		).count() > 0
	
	def save( self, mustCreate=False ):
		session = MongoSession(
			sessionKey=self.session_key,
			sessionData=self.encode(self._get_session(no_load=mustCreate)),
			expireDate=self.get_expiry_date()
		)
		try:
			session.save( forceInsert=mustCreate )
		except OperationError:
			raise CreateError

	def delete(self, session_key=None):
		if session_key is None:
			if self.session_key is None:
				return
			session_key = self.session_key
		MongoSession.objects(session_key=session_key).delete()
