# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

logging.getLogger("requests").setLevel(logging.WARNING)

