#!/usr/bin/env python
# coding=utf-8
from mailjet_rest.client import Client
from mailjet_rest.utils.version import get_version

__version__ = get_version()

__all__ = (Client, get_version)
