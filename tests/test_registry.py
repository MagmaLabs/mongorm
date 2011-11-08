from mongorm import *

def test_same( ):
	class Test(Document):
		pass
	backupTest = Test
	
	class Test(Document):
		pass
	
	assert Test == backupTest

def test_clear( ):
	class Test(Document):
		pass
	backupTest = Test
	
	DocumentRegistry.clear( )
	
	class Test(Document):
		pass
	
	assert Test != backupTest