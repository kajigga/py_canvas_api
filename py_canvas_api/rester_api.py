# -*- coding: utf-8 -*-
import requests
from .common import log

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

  def __call__(self, attr=None):
    if attr:
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

  def post(self, data={}, do_json=True, **kwargs):
    path = '/'.join(self.current_path)
    if type(data) == dict and do_json:
      http_headers = {'Content-Type': 'application/json'}
      _data = json.dumps(data)
    else:
      http_headers = {}
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


class Paginates(object):
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

    for x in self.iter_list_or_dict(res.json(), kwargs.get('keyword')):
      yield x

    if 'next' in res.links:
      while 'next' in res.links:
        res = self.req(None, full_url=res.links['next']['url'])
        for x in self.iter_list_or_dict(res.json(), kwargs.get('keyword')):
          yield x
  
  def get_paginated_dict(self, keyword, *args, **kwargs):
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

    for x in self.iter_list_or_dict(res.json(), keyword):
      yield x

    if 'next' in res.links:
      while 'next' in res.links:
        res = self.req(None, full_url=res.links['next']['url'])
        for x in self.iter_list_or_dict(res.json(), keyword):
          yield x

  def iter_list_or_dict(self, _list, keyword=None):
      if type(_list) == list:
        for r in _list:
          yield r
      else:
        #print(_list)
        if keyword:
          for r in _list[keyword]:
            yield r
        else:
          print(_list)
          return None
