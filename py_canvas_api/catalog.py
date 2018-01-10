import requests
from .rester_api import ResterAPI, Paginates, log

class Catalog(ResterAPI, Paginates):
    
  def __init__(self, base_url, *args, **kwargs):
    base_url += kwargs.get('prefix','/api/v1')
    super(Catalog, self).__init__(base_url, *args, **kwargs)

  def req(self, url, http_method="GET", full_url=None, post_body=None, http_headers={}, **kwargs):
    if not full_url:
      build_url = self.base_url.format(url)
    else:
      build_url = full_url
    headers = self.headers.copy()
    
    headers.update(http_headers)
    headers['Authorization'] = 'Token token={}'.format(self.kwargs.get('CATALOG_ACCESS_TOKEN'))

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

    log.debug('req kwargs %s', kwargs)
    return method(build_url, headers=headers, data=post_body, **kwargs)


