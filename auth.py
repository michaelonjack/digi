#!/usr/bin/env python3

from helpers import get_input, get_config

def getMovieDBKey():
	# Get client ID, secret, and access and refresh tokens from auth.ini
	config = get_config()
	config.read('auth.ini')
	moviedb_key = config.get('api_keys', 'moviedb_key')
 
	return moviedb_key
	
	
# If you want to run this as a standalone script, so be it!
if __name__ == "__main__":
	getMovieDBKey()
	print 'success!\n'

	
