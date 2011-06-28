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
import urllib
import base64


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
PAGE_DELETED=6
PAGE_NOT_FOUND=7
AUTH_REQUIRED=8
AUTH_ERROR=9
PAGE_MODIFIED=10
PAGE_NAME_MODIFIED=11

class PageNameError(Exception):
	pass

class PasswordError(Exception):
	pass

class TitleError(Exception):
	pass

class FormatError(Exception):
	pass

class ResponseError(Exception):
	pass

def HttpConnection():
	return httplib.HTTPConnection(PENIO_HOST)

def make_headers(key, create=False, user=None, password=None):
	"""
Returns a dictionary with http headers
	"""
	assert isinstance(key, str)
	headers = {}
	headers.update({"api-key": key})
	if create:
		headers.update({"Content-type": "application/x-www-form-urlencoded"})
	if user and password:
		b64s = base64.encodestring("%s:%s" % (user, password))[:-1]
		headers.update({"Authorization": "Basic %s" % b64s})
	return headers

def validate_name(page_name):
	"""
Returns true if the page name is valid.
	"""
	assert isinstance(page_name, unicode)
	if len(page_name) < MIN_NAME or len(page_name) > MAX_NAME:
		raise PageNameError()
	return True

def validate_password(password):
	"""
Returns true if the password is valid.
	"""
	assert isinstance(password, unicode)
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
	exit_codes = {
		404: PAGE_AVAILABLE,
		200: PAGE_EXISTS,
	}
	validate_name(page_name)
	conn = HttpConnection()
	path = "/pages/%s" % page_name
	headers = make_headers(key)
	conn.request("HEAD", path, headers=headers)
	response = conn.getresponse()
	try:
		return exit_codes[response.status]
	except KeyError:
		raise ResponseError()

def create_page(key, page_name, password, title=u"", content=u""):
	"""
Creates a new page in the server
	"""
	exit_codes = {
		201: PAGE_CREATED,
		409: PAGE_CONFLICT,
		412: VALIDATION_ERROR,
	}
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
	try:
		return exit_codes[response.status]
	except KeyError:
		raise ResponseError()

def update_page(key, page_name, password, title=u"", content=u""):
	"""
Changes the contents of a page
	"""
	exit_codes = {
		204: PAGE_MODIFIED,
		301: PAGE_NAME_MODIFIED,
		409: PAGE_CONFLICT,
		412: VALIDATION_ERROR,
		404: PAGE_NOT_FOUND,
		401: AUTH_REQUIRED,
		403: AUTH_ERROR,
	}
	validate_name(page_name)
	validate_password(password)
	conn = HttpConnection()
	path = "/pages/%s" % page_name
	headers = make_headers(key, user=page_name, password=password)
	params_dict = {}
	if title != u"":
		validate_title(title)
		params_dict.update({"title": title})
	if content != u"":
		params_dict.update({"content": content})
	params = urllib.urlencode(params_dict)
	conn.request("PUT", path, params, headers)
	response = conn.getresponse()
	try:
		return exit_codes[response.status]
	except KeyError:
		raise ResponseError()

def delete_page(key, page_name, password):
	"""
Deletes a page from the server
	"""
	exit_codes = {
		204: PAGE_DELETED,
		404: PAGE_NOT_FOUND,
		401: AUTH_REQUIRED,
		403: AUTH_ERROR,
	}
	validate_name(page_name)
	validate_password(password)
	conn = HttpConnection()
	path = "/pages/%s" % page_name
	headers = make_headers(key, user=page_name, password=password)
	conn.request("DELETE", path, headers=headers)
	response = conn.getresponse()
	try:
		return exit_codes[response.status]
	except KeyError:
		raise ResponseError()

def get_page(key, page_name, password=None, page_format=""):
	"""
If the page exists, it is returned in the chosen format, or html if no format
is specified.
	"""
	exit_codes = {
		404: PAGE_NOT_FOUND,
		401: AUTH_REQUIRED,
		403: AUTH_ERROR,
	}
	validate_name(page_name)
	conn = HttpConnection()
	if page_format in ("", "html"):
		path = "/pages/%s" % page_name
	elif page_format in ('json', 'xml'):
		path = "/pages/%s/%s" % (page_name, page_format)
	else:
		raise FormatError()
	if password:
		validate_password(password)
		headers = make_headers(key, user=page_name, password=password)
	else:
		headers = make_headers(key)
	conn.request("GET", path, headers=headers)
	response = conn.getresponse()
	if response.status == 200:
		return response.read()
	else:
		try:
			return exit_codes[response.status]
		except KeyError:
			raise ResponseError()
