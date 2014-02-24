"""These functions should not depend on external state"""
import binascii, os

from flask import session


def generate_csrf_token():
    """Modifies sessions returns csrf token @_@"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = binascii.b2a_hex(os.urandom(20))
    return session['_csrf_token']

