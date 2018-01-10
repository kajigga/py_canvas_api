# -*- coding: utf-8 -*-
import os
from .canvas_api import Canvas
from .common import log

class SISImporter(object):
  def __init__(self, canvas_domain, canvas_token):
    self.canvas_api = Canvas(canvas_domain, CANVAS_ACCESS_TOKEN=canvas_token)
    self.last_sis_import = None
    self.sis_imports = {}

  def wait_for_done(self, import_id=None):
    """Wait for the given import_id to be done, then return the import"""
    while self.sis_imports[import_id]['workflow_state'] in RUNNING_STATES:
      # Consider putting a delay here
      self.check_sis_import(import_id)
    return self.sis_imports[import_id]

  def check_sis_import(self, import_id):
    '''Check the sis_import given by `import_id`'''

    # Protect against a non-existent import_id
    if import_id in self.sis_imports:
      self.sis_imports[import_id] = self.canvas_api.accounts('self').sis_imports(import_id).get().json()
      return self.sis_imports[import_id]
    

  def do_sis_import(self, 
      filepath, 
      import_type='instructure_csv', 
      **kwargs):
    """ Do an SIS Import with the given file. A variety of options can be
    given.

    >>> sis_importer = SISImporter('test.instructure.com', CANVAS_ACCESS_TOKEN=token)
    >>> sis_importer.do_sis_import('./test.csv')
    """
    
    body = dict(
      import_type=import_type,
      #attachment=open(filepath,'r').read(),
      extension=os.path.splitext(filepath)[-1][-3:],
      change_threshold=kwargs.get('change_threshold', None) # Required for multi_term_batch_mode
    )

    # Check for stickiness
    if kwargs.get('override_sis_stickiness', False):
      body['override_sis_stickiness'] = kwargs.get('override_sis_stickiness', False)
      body['add_sis_stickiness'] = kwargs.get('add_sis_stickiness', False)
      body['clear_sis_stickiness'] = kwargs.get('clear_sis_stickiness', False)

    # Check for Batch mode
    if kwargs.get('batch_mode', False):
      body['batch_mode'] = kwargs.get('batch_mode', False)
      body['batch_mode_term_id'] = kwargs.get('batch_mode_term_id')
      body['multi_term_batch_mode'] = kwargs.get('multi_term_batch_mode', False)
      if body['multi_term_batch_mode'] and not body.get('change_threshold'):
        body['change_threshold']=kwargs.get('change_threshold', 100) # Required for multi_term_batch_mode

    # Check For diffing
    if kwargs.get('diffing_data_set_identifier', None):
      body['diffing_data_set_identifier'] = kwargs.get('diffing_data_set_identifier', None)
      body['diffing_remaster_data_set'] = kwargs.get('diffing_remaster_data_set')
      body['diffing_drop_status'] = kwargs.get('diffing_drop_status')	#Allowed values: deleted, completed, inactive

    files = {'attachment': open(filepath, 'rb')}
    sis_import = self.canvas_api.accounts('self').sis_imports.post(data=body, do_json=False, files=files).json()
    self.sis_imports[sis_import['id']] = sis_import
    return sis_import

