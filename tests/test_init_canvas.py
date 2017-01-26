import os
from unittest import TestCase
try:
  from unittest.mock import MagicMock, call
except:
  #from mock import MagicMock, call
  pass

import json
import requests

import canvas_api
BASE_URL = 'kevin.test.instructure.com'
CANVAS_ACCESS_TOKEN='1~7GxKeS9cqHcNQxzKAZBhot6qurrWsJrYhPJiTY71lqxj37peuccu0ESl4fXh1VRL'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestPyCanvasAPI(TestCase):
  def setUp(self):
    self.c_api = canvas_api.Canvas(BASE_URL, CANVAS_ACCESS_TOKEN=CANVAS_ACCESS_TOKEN)
    self.c_api.req = MagicMock()

  def test_get_calls(self):

    # Should call /accounts/self/courses?page=2
    self.c_api.accounts('self').courses.get(**{'page':2})
    self.c_api.req.assert_called_with('accounts/self/courses', params={'page':2})


    # Should call /accounts/self/authentication_configs
    self.c_api.accounts('self').authentication_configs.get()
    self.c_api.req.assert_called_with('accounts/self/authentication_configs', params={})

    # Should call /accounts/25/courses?page=2
    self.c_api.accounts('25').courses.get(**{'page':2})
    self.c_api.req.assert_called_with('accounts/25/courses', params={'page':2})

  def test_post_calls(self):
    # This should test making post calls
    course = dict( 
      name="test course",
      course_code="test course",
      term_id="term_id_1001",
      sis_course_id="test_course_term_1001")

    self.c_api.accounts('25').courses.post(data=course)
    self.c_api.req.assert_called_with('accounts/25/courses', 
        post_body=json.dumps(course), 
        http_headers={'Content-Type': 'application/json'}, 
        http_method='POST')

  def test_upload_file(self):
    # TODO how do I mock this?
    pass

class TestCommonsAPI(TestCase):
  def setUp(self):
    self.commons = canvas_api.Commons(BASE_URL, CANVAS_ACCESS_TOKEN=CANVAS_ACCESS_TOKEN)
    self.jwt_response = { "jwt_token": "eyJ0eXAiOiJ"}
    self.session_response = { "sessionId": u"lkjlklkjlkj"}

    #self.commons.canvas2.req = MagicMock()
    res_list = json.load(open(os.path.join(BASE_DIR, 'resources_list.json'),'rU'))
    requests.get = MagicMock()
    requests.get.side_effect = [
        MagicMock(status_code=200, text=json.dumps(self.jwt_response), json=lambda: self.jwt_response),
        MagicMock(status_code=200, text=json.dumps(res_list), json=lambda: res_list),
    ]

    requests.post = MagicMock()
    requests.post.side_effect = [
        MagicMock(status_code=200, text=json.dumps(self.session_response), json=lambda: self.session_response)
        ]


  def test_get_jwt_token(self):
    jwt_token = self.commons.get_jwt_token()
    assert jwt_token == self.jwt_response

  def test_get_session_id(self):

    self.assertEqual(self.commons.get_session_id(), self.session_response['sessionId'])

  def test_list_resources(self):

    resources = self.commons.resources.get().json()

    requests.get.assert_has_calls([call('https://lor.instructure.com/api/resources', data=None, headers={'X-Session-ID': u'lkjlklkjlkj'}, params={})])
    requests.post.assert_has_calls([call('https://lor.instructure.com/api/sessions', data='{"jwt_token": "eyJ0eXAiOiJ"}', headers={'Content-Type': 'application/json'})])

    self.assertIsInstance(resources, dict)
    self.assertEqual(resources.keys(), {'items':[],'meta':{}}.keys())
