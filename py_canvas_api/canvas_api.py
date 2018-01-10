# -*- coding: utf-8 -*-
import json, os
import requests
import collections
import mimetypes
from .rester_api import ResterAPI, Paginates
from .common import log

class Canvas(ResterAPI, Paginates):


  def __init__(self, base_url, *args, **kwargs):
    '''
    Instantiate the Canvas object like this.
    >>> c = Canvas('somedomain.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('ACCESS_TOKEN'))
    '''
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

    log.debug('build_url %s', build_url)
    log.debug('post_body %s', post_body)
    log.debug('http_headers %s', http_headers)
    log.debug('headers %s', headers)
    log.debug('req kwargs %s', kwargs)
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



  def _get_upload_params(self, filepath, parent_folder_path=None, **kwargs):

    mime_type, encoding = mimetypes.guess_type(filepath)

    filename = os.path.basename(filepath)
    inform_parameters = {
      'name': filename,

      'size': os.path.getsize(filepath), # read the filesize
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

    json_res = json.loads(res.text, object_pairs_hook=collections.OrderedDict)

    # Upload file
    # Upload confirmation is handled if you let the upload follow redirects
    log.info('-json_res- %s', json_res)
    upload_file_response = requests.post(
        json_res['upload_url'], 
        data=list( list(json_res.items())[1][1].items()), 
        files={'file':open(filepath,'rb')}, 
        params=kwargs,
        allow_redirects=True).json()

    log.info("Upload completed...nicely done!")
    log.debug('upload response %s', upload_file_response)
    return upload_file_response



if __name__ == '__main__':
  c = Canvas('<domain_here>.instructure.com', CANVAS_ACCESS_TOKEN=os.getenv('CANVAS_ACCESS_TOKEN'))
  
  upload_params = c._get_upload_params('./requirements.txt', parent_folder_path='testingfiles')
  upload_started = c.courses('<course_id_here>').files.post(data=upload_params)
  c.upload_file(upload_started, './requirements.txt')
