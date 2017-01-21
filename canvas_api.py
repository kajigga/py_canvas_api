# -*- coding: utf-8 -*-
import json, os
import requests

import csv
import collections
import time,logging
import itertools

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

logging.getLogger("requests").setLevel(logging.WARNING)

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


  def delete(self, body={}):
    path = '/'.join(self.current_path)
    json_res = self.req(path, http_method='DELETE', post_body=body)
    self.reset()
    return json_res

  def req(self, url, http_method="GET", post_body=None, http_headers={}, **kwargs):
    return NotImplented

class Canvas(ResterAPI):

  def __init__(self, base_url, *args, **kwargs):
    base_url += '/api/v1/'
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

  def get_paginated(self, paginate=False, **kwargs):
    current_path = self.current_path
    res = self.get(**kwargs)
    try:
      res.json()
    except Exception as exc:
      log.error('problem reading response: {} - status: {}'.format(self.current_path, res.status_code))
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

