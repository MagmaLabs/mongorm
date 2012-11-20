from pymongo import Connection

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

connectionSettings = []

def connect( database, **kwargs ):
	connectionSettings.append( ConnectionSettings( database, **kwargs ) )

class pushDatabase(object):
	def __init__( self, database, **kwargs ):
		self.settings = ConnectionSettings( database, **kwargs )
	
	def __enter__( self ):
		#print '>>> entering database', self.settings.connectionSettings
		connectionSettings.append( self.settings )
	
	def __exit__( self, type, value, traceback ):
		connectionSettings.pop( )
		#print '<<< existing database'

def getConnection( ):
	assert len(connectionSettings) > 0, "No database specified: call mongorm.connect() before use"
	
	return connectionSettings[-1].getConnection( )

def getDatabase( ):
	assert len(connectionSettings) > 0, "No database specified: call mongorm.connect() before use"
	
	return connectionSettings[-1].getDatabase( )