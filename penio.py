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

import httplib, urllib

PENIO_HOST = "pen.io"
MIN_NAME = 2
MAX_NAME = 60
MIN_PWD = 1
MAX_PWD = 30
MIN_TITLE = 1
MAX_TITLE = 255

## exit codes
PAGE_EXISTS=1
PAGE_AVAILABLE=2
PAGE_CREATED=3
PAGE_CONFLICT=4
VALIDATION_ERROR=5

class PageNameError(Exception):
	pass

class PasswordError(Exception):
	pass

class TitleError(Exception):
	pass

class ResponseError(Exception):
	pass

def HttpConnection():
	return httplib.HTTPConnection(PENIO_HOST)

def make_headers(key, create=False):
	"""
Returns a dictionary with http headers
	"""
	assert isinstance(key, str)
	headers = {}
	headers.update({"api-key": key})
	if create:
		headers.update({"Content-type": "application/x-www-form-urlencoded"})
	return headers

def validate_name(page_name):
	"""
Returns true if the page name is valid.
	"""
	assert isinstance(page_name, str)
	if len(page_name) < MIN_NAME or len(page_name) > MAX_NAME:
		raise PageNameError()
	return True

def validate_password(password):
	"""
Returns true if the password is valid.
	"""
	assert isinstance(password, str)
	if len(password) < MIN_PWD or len(password) > MAX_PWD:
		raise PasswordError()
	return True

def validate_title(title):
	"""
Returns true if the title is valid.
	"""
	assert isinstance(title, unicode)
	if len(title) < MIN_TITLE or len(title) > MAX_TITLE:
		raise TitleError()
	return True

def check_page(key, page_name):
	"""
Returns true if the page exists, false if it doesn't
	"""
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

def create_page(key, page_name, password, title=u"", content=u""):
	"""
Creates a new page in the server
	"""
	validate_name(page_name)
	validate_password(password)
	conn = HttpConnection()
	path = "/pages"
	headers = make_headers(key, create=True)
	params_dict = {
		"page_name": page_name,
		"password": password,
	}
	if title != u"":
		validate_title(title)
		params_dict.update({"title": title})
	if content != u"":
		params_dict.update({"content": content})
	params = urllib.urlencode(params_dict)
	conn.request("POST", path, params, headers)
	response = conn.getresponse()
	if response.status == 201:
		return PAGE_CREATED
	elif response.status == 409:
		return PAGE_CONFLICT
	elif response.status == 412:
		return VALIDATION_ERROR
	else:
		raise ResponseError

