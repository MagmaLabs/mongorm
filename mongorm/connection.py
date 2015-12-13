try:
	from pymongo import Connection
except:
	from pymongo import MongoClient
	Connection = MongoClient

class ConnectionSettings(object):
	def __init__( self, database, **kwargs ):
		connectionSettings = {}
		connectionSettings.update( kwargs )
		connectionSettings.update( {
			'database': database
		} )
		
		self.connectionSettings = connectionSettings
		self.connection = None
		self.database = None
	
	def getConnection( self ):
		assert self.connectionSettings is not None, "No database specified: call mongorm.connect() before use"

		if self.connection is None:
			connectionArgs = {}

			for key in ['host', 'port']:
				if key in self.connectionSettings:
					connectionArgs[key] = self.connectionSettings[key]

			self.connection = Connection( **connectionArgs )

		return self.connection

	def getDatabase( self ):
		if self.database is None:
			connection = self.getConnection( )
			databaseName = self.connectionSettings['database']
			self.database = connection[databaseName]

			if 'username' in self.connectionSettings and \
				'password' in self.connectionSettings:
				self.database.authenticate( self.connectionSettings['username'], self.connectionSettings['password'] )

		return self.database

connectionSettings = {}

def _pushConnection( settings, groupName ):
	connectionSettings.setdefault( groupName, [] ).append( settings )

def _popConnection( groupName ):
	return connectionSettings[groupName].pop( )

def connect( database, groupName='default', **kwargs ):
	_pushConnection( ConnectionSettings( database, **kwargs ), groupName )

class pushDatabase(object):
	def __init__( self, database, groupName='default', **kwargs ):
		self.groupName = groupName
		self.settings = ConnectionSettings( database, **kwargs )
	
	def __enter__( self ):
		#print '>>> entering database', self.settings.connectionSettings
		_pushConnection( self.settings, self.groupName )
	
	def __exit__( self, type, value, traceback ):
		_popConnection( self.groupName )
		#print '<<< existing database'

def getConnection( groupName='default' ):
	assert len(connectionSettings.get(groupName,[])) > 0, "No database specified for database group '%s': call mongorm.connect() before use" % groupName
	
	return connectionSettings[groupName][-1].getConnection( )

def getDatabase( groupName='default' ):
	assert len(connectionSettings.get(groupName,[])) > 0, "No database specified for database group '%s': call mongorm.connect() before use" % groupName
	
	return connectionSettings[groupName][-1].getDatabase( )
