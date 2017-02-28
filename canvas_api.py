# -*- coding: utf-8 -*-
import json, os
import requests

import csv
import collections
import time,logging

import mimetypes
import collections

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

logging.getLogger("requests").setLevel(logging.WARNING)
#logging.getLogger("requests").setLevel(logging.DEBUG)

class ResterAPI(object):
  def __init__(self, base_url, **kwargs):
    self.current_path = []
    self.headers = {}
    if base_url:
      base_url = list(base_url)
      if base_url[-1] != '/':
        base_url.append('/')

      if base_url[:7] == 'http://':
        base_url.insert(7,'s')
      if base_url[:8] != 'https://':
        base_url.insert(0,'https://')

    self.base_url = ''.join(base_url) + '{}'
    self.kwargs = kwargs

  def __call__(self, attr):
    self.current_path.append(str(attr))
    return self

  def __getattr__(self, name):
    self.current_path.append(name)

    return self

  def reset(self):
    self.current_path = []

  def get(self, **kwargs):
    '''
    Make the api call, returning the Response object from the requests module.

    >>> c = Canvas('someodmain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))
    >>> user_987 = c.accounts('self').users(987).get()
    >>> user_987.json()
    {
        'id':987,
        etc...
        }

    '''
    path = '/'.join(self.current_path)
    json_res = self.req(path, params=kwargs)
    self.reset()
    return json_res

  def post(self, data={}, **kwargs):
    path = '/'.join(self.current_path)
    http_headers = {'Content-Type': 'application/json'}
    if type(data) == dict:
      _data = json.dumps(data)
    else:
      _data = data
    json_res = self.req(path, 
        http_method='POST', 
        post_body=_data,
        http_headers=http_headers,
        **kwargs)
    self.reset()
    return json_res

  def put(self, data, **kwargs):
    path = '/'.join(self.current_path)
    http_headers = {'Content-Type': 'application/json'}
    json_res = self.req(path, 
        http_method='PUT', 
        params=kwargs,
        post_body=json.dumps(data), 
        http_headers=http_headers)
    self.reset()
    return json_res


  def delete(self, body={}, **kwargs):
    path = '/'.join(self.current_path)
    json_res = self.req(path, http_method='DELETE', post_body=body)
    self.reset()
    return json_res

  def req(self, url, http_method="GET", post_body=None, http_headers={}, **kwargs):
    return NotImplemented

class Canvas(ResterAPI):

  def __init__(self, base_url, *args, **kwargs):
    base_url += kwargs.get('prefix','/api/v1')
    super(Canvas, self).__init__(base_url, *args, **kwargs)

  def req(self, url, http_method="GET", full_url=None, post_body=None, http_headers={}, **kwargs):
    if not full_url:
      build_url = self.base_url.format(url)
    else:
      build_url = full_url
    headers = self.headers.copy()
    
    headers.update(http_headers)
    headers['Authorization'] = 'Bearer {}'.format(self.kwargs.get('CANVAS_ACCESS_TOKEN'))
    # Default is GET
    method = requests.get
    if http_method == 'GET':
      method = requests.get
    elif http_method == 'POST':
      method = requests.post
    elif http_method == 'PUT':
      method = requests.put
    elif http_method == 'DELETE':
      method = requests.delete

    return method(build_url, headers=headers, data=post_body, **kwargs)


  def get_paginated(self, *args, **kwargs):
    '''Requests all pages of a paginated result.

    >>> c = Canvas('someodmain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))
    >>> all_users = c.accounts('self').users.get_paginated()

    '''
    current_path = self.current_path
    log.info('current_path %s', '/'.join(current_path))
    res = self.get(**kwargs)
    try:
      res.json()
    except Exception as exc:
      log.error('problem reading response: {} - status: {}'.format(current_path, res.status_code))
      yield []

    if type(res.json()) != list:
      yield res
    else:
      for r in res.json():
        yield r
      while 'next' in res.links:
        res = self.req(None, full_url=res.links['next']['url'])
        for r in res.json():
          yield r
  
  def _get_upload_params(self, filepath, parent_folder_path=None, **kwargs):

    mime_type, encoding = mimetypes.guess_type(filepath)

    filename = os.path.basename(filepath)
    inform_parameters = {
      'name': filename,
      'size': os.path.getsize(filename), # read the filesize
      'content_type': mime_type,
      'parent_folder_path': parent_folder_path
       }

    inform_parameters.update(**kwargs)
    return inform_parameters


  # Written to take the response of the initial post request
  # that needs a file upload. This request will usually take, among other query
  # and post parameters, parameters related to the file upload itself.
  # name : The filename of the file. Any UTF-8 name is allowed. Path components such as `/` and `\` will be treated as part of the filename, not a path to a sub-folder.
  # size : The size of the file, in bytes. This field is recommended, as it will let you find out if there's a quota issue before uploading the raw file.
  # content_type : The content type of the file. If not given, it will be guessed based on the file extension.
  # parent_folder_id : The id of the folder to store the file in. If this and parent_folder_path are sent an error will be returned. If neither is given, a default folder will be used.
  # parent_folder_path : The path of the folder to store the file in. The path separator is the forward slash `/`, never a back slash. The folder will be created if it does not already exist. This parameter only applies to file uploads in a context that has folders, such as a user, a course, or a group. If this and parent_folder_id are sent an error will be returned. If neither is given, a default folder will be used.
  # on_duplicate : How to handle duplicate filenames. If `overwrite`, then this file upload will overwrite any other file in the folder with the same name. If `rename`, then this file will be renamed if another file in the folder exists with the given name. If no parameter is given, the default is `overwrite`. This doesn't apply to file uploads in a context that doesn't have folders.
  def upload_file(self, res, filepath, **kwargs):
    """This method will upload a file to canvas. It requires the initial
    response from a file upload endpoint and the filepath itself.


    >>> c = Canvas('someodmain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))
    >>> upload_started = c.courses(123423).files.post(file_upload_params)
    >>> c.upload_file(upload_started, './requirements.txt') # When this is done, the file is uploaded

    Known places where an upload starts:

      * /api/v1/courses/:course_id/files
      * /api/v1/folders/:folder_id/files
      * /api/v1/groups/:group_id/files
      * /api/v1/users/:user_id/files
      * /api/v1/courses/:course_id/quizzes/:quiz_id/submissions/self/files
      * /api/v1/courses/:course_id/assignments/:assignment_id/submissions/self/files
      * /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/comments/files
      * /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/files
      * /api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/files
      * /api/v1/accounts/:account_id/content_migrations
      * /api/v1/courses/:course_id/content_migrations
      * /api/v1/groups/:group_id/content_migrations
      * /api/v1/users/:user_id/content_migrations
    """

    logging.info("Yes! Done sending pre-emptive 'here comes data' data, now uploading the file...")
    json_res = json.loads(res.text, object_pairs_hook=collections.OrderedDict)

    # Upload file
    # Upload confirmation is handled if you let the upload follow redirects
    upload_file_response = requests.post(
        json_res['upload_url'], 
        data=list( list(json_res.items())[1][1].items()), 
        files={'file':open(filepath,'rb')}, 
        allow_redirects=True)

    logging.info("Upload completed...nicely done!")

class Commons(ResterAPI):
  def __init__(self, base_url, *args, **kwargs):
    kwargs['prefix'] = '/api/lti'
    self.canvas2 = Canvas(base_url, *args, **kwargs)
    self._session_id = None

    super(Commons, self).__init__('lor.instructure.com/api', *args, **kwargs)

  def req(self, url, http_method="GET", full_url=None, post_body=None, http_headers={}, **kwargs):
    if not full_url:
      build_url = self.base_url.format(url)
    else:
      build_url = full_url
    headers = self.headers.copy()
    
    headers.update(http_headers)
    headers['X-Session-ID'] = self.get_session_id()
    # Default is GET
    method = requests.get
    if http_method == 'GET':
      method = requests.get
    elif http_method == 'POST':
      method = requests.post
    elif http_method == 'PUT':
      method = requests.put
    elif http_method == 'DELETE':
      method = requests.delete

    res = None
    try:
      res = method(build_url, headers=headers, data=post_body, **kwargs)
    except Exception as exc:
      log.error('{}'.format(exc))
      # Canvas should be reset if an error occurs
      self.reset()
    return res

      

  def req_session_id(self, data, **kwargs):
    build_url = self.base_url.format('sessions')

    http_headers = {'Content-Type': 'application/json'}

    res = requests.post(build_url, headers=http_headers, data=json.dumps(data))
    return res.json()

  def get_jwt_token(self):
    res = self.canvas2.accounts('self').jwt_token.get(
        tool_launch_url='https://lor.instructure.com/api/lti')

    return res.json()

  def get_session_id(self):
    if not self._session_id:
      # Make request to canvas to get jwt_token
      jwt_token = self.get_jwt_token()
      # Make request to start session endpoint

      session = self.req_session_id(data=jwt_token)
      if session['sessionId']:
        self._session_id = session['sessionId']
    return self._session_id
  


if __name__ == '__main__':
  c = Canvas('<domain_here>.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('CANVAS_ACCESS_TOKEN'))
  
  upload_params = c._get_upload_params('./requirements.txt', parent_folder_path='testingfiles')
  upload_started = c.courses('<course_id_here>').files.post(data=upload_params)
  c.upload_file(upload_started, './requirements.txt')
