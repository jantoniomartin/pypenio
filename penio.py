##
## penio.py
## 
## (c) 2011 Jose Antonio Martin Prieto
##
## This file defines interface functions to access the pen.io API.
## To use the functions, you must get an API key, that should be passed as a
## parameter.
## The API key may be got in http://pen.io/gen_api_key.php
##

import httplib

PENIO_HOST = "pen.io"
MIN_NAME = 2
MAX_NAME = 60
MIN_PWD = 1
MAX_PWD = 30

## exit codes
PAGE_EXISTS=1
PAGE_AVAILABLE=2

class PageNameError(Exception):
	pass

class ResponseError(Exception):
	pass

def HttpConnection():
	return httplib.HTTPConnection(PENIO_HOST)

def make_headers(key):
	"""
Returns a dictionary with http headers
	"""
	assert isinstance(key, str)
	headers = {}
	headers.update({"api-key": key})
	return headers

def validate_name(page_name):
	"""
Returns true if the page name is valid.
	"""
	assert isinstance(page_name, str)
	if len(page_name) < MIN_NAME or len(page_name) > MAX_NAME:
		raise PageNameError()
	return True

def check_page(key, page_name):
	"""
Returns true if the page exists, false if it doesn't
	"""
	assert isinstance(page_name, str)
	validate_name(page_name)
	conn = HttpConnection()
	path = "/pages/%s" % page_name
	headers = make_headers(key)
	conn.request("HEAD", path, headers=headers)
	response = conn.getresponse()
	if response.status == 404:
		return PAGE_AVAILABLE
	elif response.status == 200:
		return PAGE_EXISTS
	else:
		raise ResponseError()

