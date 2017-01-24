from unittest import TestCase
from mock import MagicMock

import canvas_api
BASE_URL = 'test.instructure.com'
CANVAS_ACCESS_TOKEN='lkjlkjlkj'

class TestPyCanvasAPI(TestCase):
  def setUp(self):
    self.c_api = canvas_api.Canvas(BASE_URL, CANVAS_ACCESS_TOKEN=CANVAS_ACCESS_TOKEN)
    self.c_api.req = MagicMock()

  def test_get_calls(self):

    # Should call /accounts/self/courses?page=2
    self.c_api.accounts('self').courses.get(**{'page':2})
    self.c_api.req.assert_called_with('accounts/self/courses', params={'page':2})

    # Should call /accounts/25/courses?page=2
    self.c_api.accounts('25').courses.get(**{'page':2})
    self.c_api.req.assert_called_with('accounts/25/courses', params={'page':2})

    # Should call /accounts/self/authentication_configs
    self.c_api.accounts('self').authentication_configs.get()
    self.c_api.req.assert_called_with('accounts/self/authentication_configs', params={})

  def test_post_calls(self):
    # This should test making post calls
    pass

  def test_delete_calls(self):
    # This should test making delete calls
    pass

  def test_put_calls(self):
    # This should test making put calls
    pass
