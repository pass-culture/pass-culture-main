"""
This module manages the session lifecycle. The only public methods in this module are those declared
in this file
"""

from ._backoffice import install_login as install_backoffice_login
from ._mingled import install_login as install_mingled_login


__all__ = [
    "install_mingled_login",
    "install_backoffice_login",
]
