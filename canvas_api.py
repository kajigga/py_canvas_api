# -*- coding: utf-8 -*-
import json, os
import requests

import csv
import collections
import time,logging
import itertools
import zipfile

#from poster.encode import multipart_encode
#from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler
#import urllib2
spinner = itertools.cycle(['-', '/', '|', '\\'])

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


migration_types = {
  "angel_exporter": {
    "type": "angel_exporter",
    "name": "Angel export .zip format",
  },
  "blackboard_exporter": {
    "type": "blackboard_exporter",
    "name": "Blackboard 6/7/8/9 export .zip file",
  },
  "webct_scraper": {
    "type": "webct_scraper",
    "name": "Blackboard Vista/CE, WebCT 6+ Course",
  },
  "canvas_cartridge_importer": {
    "type": "canvas_cartridge_importer",
    "name": "Canvas Course Export Package",
  },
  "common_cartridge_importer": {
    "type": "common_cartridge_importer",
    "name": "Common Cartridge 1.0/1.1/1.2 Package",
  },
  "d2l_exporter": {
    "type": "d2l_exporter",
    "name": "D2L export .zip format",
  },
  "moodle_converter": {
    "type": "moodle_converter",
    "name": "Moodle 1.9 .zip file",
  }
}
try:
  # NOTE - if you install the clint pypi library you will get a nice progress
  # bar during script execution.
  from clint.textui.progress import Bar
except:
  class Bar(object):
    def __init__(self,*args,**kwargs):
      self.label = kwargs.get('label','')
    def show(self,idx):
      print("{0.label} {1}% done".format(self,idx))

    @property
    def label(self):
      return self._label

    @label.setter
    def label(self, value):
      print(value)
      self._label = value



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

  """
  def content_migration(self, course_id, migration_type, filename, file_path):
    '''upload a file for a content migration'''


    workingPath = "/Users/kjhansen/Downloads/"; # Important! Make sure this ends with a backslash

    wait_till_done = True 

    #migration_type = "blackboard_exporter" # Change this to fit your migration type
    migration_type = "common_cartridge_importer" # Change this to fit your migration type
    process_type = 'upload' # options are 'upload' or 'link'

    # Recent options for migration_type include:

  #def massDoCopies(data):
  #def massDoCopies(self):
    # data[1] is the row of data, in the form of a list


    #folders_url = "https://{}/api/v1/courses/{}/folders".format(canvas_domain,row_data['destination_id'])

    found_course = {}

    self.reset()
    found_course = self.courses(course_id).get().json()

    if not found_course.get('id',None):
      log.error('course not found %s', course_id)
    else:
      log.info('course found %s', course_id)

      params = {
        'migration_type': migration_type
      }

      # Course quota size checking
      z = zipfile.ZipFile(open(file_path,'rb'))
      uncompress_size_mb = sum((file.file_size for file in z.infolist()))/1000000.0
      # Get course quota via api
      # Get the course used quota
      #/api/v1/courses/:course_id/files/quota

      self.reset()
      course_quota_info = self.courses(course_id).files.quota.get().json()

      # if it isn't large enough for the unzipped
      # files then increase it to current usage + uncompress_size + 50%
      if not ((course_quota_info['quota'] - course_quota_info['quota_used'])/1000000.0) > uncompress_size_mb:
        # Increase the space needed
        update_course_data = {'course[storage_quota_mb]':course_quota_info['quota']+uncompress_size_mb}

        # TODO Redo this
        # course_quota_info = requests.put(course_search_url,data=update_course_data,headers=headers).json()

      # TODO Pre-upload content package checking according to the type.
      # TODO Get list of common errors from Tdoxey
      params['pre_attachment']={
        'name': filename,
        'size':os.path.getsize(file_path), # read the filesize
        'content_type':'application/zip',
       }

      #if migration_type == 'zip_file_importer':
      #  folder_info = {'name': row_data['source_id']}
      #  folder = requests.post(folders_url, headers=headers, data=folder_info).json()
      #  log.info('******** this is a zip file importer, new folder %s', folder.get('id'))
      #  params['settings'] = {'folder_id' : folder.get('id') }


      #uri = "https://{}/api/v1/courses/{}/content_migrations".format(canvas_domain,row_data['destination_id'])

      self.reset()
      migration = self.courses(course_id).content_migrations.post(params)
      migration_json = migration.json()

      log.debug(migration.json())

      log.info("Done prepping Canvas for upload, now sending the data...")
      json_res = json.loads(migration.text,object_pairs_hook=collections.OrderedDict)


      # Step 2:  Upload data
      files = {'file':open(file_path,'rb').read()}
      
      log.info('-------- json_keys1 --- %s', json_res.keys())
      if json_res.has_key('message'):
        log.error( json_res['message'])
      else:
        _data = json_res['pre_attachment'].items()
        if _data[1][0]=='error':
            log.error("{} - There was a problem uploading the file.  Probably a course quota problem.".format(course_id))
            return

        _data[1] = ('upload_params',_data[1][1].items())

        log.info("Yes! Done sending pre-emptive 'here comes data' data, now uploading the file...")
        log.info('-------- json_keys2 --- %s', json_res.keys())
        upload_file_response = self.uploadFile(json_res['pre_attachment'], file_path)

        # Step 3: Confirm upload

        log.info("Done uploading the file, now confirming the upload...")
        log.info("upload completed...nicely done! The Course migration should be starting soon.")

        self.reset()
        migration_json = self.courses(course_id).content_migrations(migration_json['id']).get().json()
        
      prog_url = migration_json['progress_url']
      status = self.req(prog_url, full_url=prog_url).json()
      if wait_till_done:
        last_progress = status['completion']
        while status['workflow_state'] in ('pre-processing','queued','running'):
          done_statusing = False
          while not done_statusing:
            try:
              status = self.req(prog_url, full_url=prog_url).json()
              done_statusing = True
            except Exception as err:
              log.error('{}'.format(err))

          if status['completion']!=last_progress:
            log.debug("{} {}".format(status['workflow_state'],status['completion']))
            last_progress = status['completion']
        if status['workflow_state']=='failed':
            log.info("{} - {} {}".format(course_id,status['workflow_state'],status['completion']))
            log.debug(self.req(migration_json['migration_issues_url'],full_url=migration_json['migration_issues_url']).text)
        else:
            log.info("{} - {} {}".format(course_id,status['workflow_state'],status['completion']))

      self.reset()
      migration_issues = self.courses(course_id).content_migrations(migration_json['id']).migration_issues.get().json()
      #https://kevin.instructure.com/api/v1/courses/2058266/content_migrations/873884/migration_issues
      for mi in migration_issues:
        log.debug('%s', mi['description'])
      #copyCache['sources'][source_id].append(csvrow[destination_course_id_column])
      log.info(last_progress)
      log.info('all done')

  def uploadFile(self, data, filename):

    data['upload_params']['file'] = open(filename, "rb")

    #opener = urllib2.build_opener(*[StreamingHTTPHandler, StreamingHTTPSHandler])
    #urllib2.install_opener(opener)

    #datagen, headers = multipart_encode(data['upload_params'])

    #print 'pp: data[file]',data['file']
    #request = urllib2.Request(data['upload_url'], datagen,headers)
    #result = urllib2.urlopen(request)
    request = requests.post(data['upload_url'], data=data['upload_params'], files={filename: open(filename, 'rb')})

    #response = json.load(result)
    response = request.json()
    #response.update( dict(
    #  status=result.getcode(),
    #  headers=result.info()))
    return response
    """
