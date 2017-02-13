# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
import requests
from socket import error as sock_err

log = logging.getLogger(__name__)

def get_html(url):
    """@todo: Docstring for get_html.

    :url: @todo
    :returns: @todo

    """
    log.info('Getting html from %s', url)
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except (requests.RequestException, sock_err):
        pass
    else:
        return resp.content
    return None
