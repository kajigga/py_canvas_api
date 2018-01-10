# -*- coding: utf-8 -*-
import requests
import json
from .rester_api import ResterAPI, log
from .canvas_api import Canvas

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
  


