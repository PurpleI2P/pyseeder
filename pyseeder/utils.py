"""Various code"""
import os

class PyseederException(Exception):
    pass

class TransportException(PyseederException):
    pass

def check_readable(f):
    """Checks if path exists and readable"""
    if not os.path.exists(f) or not os.access(f, os.R_OK):
        raise PyseederException("Error accessing path: {}".format(f))

def check_writable(f):
    """Checks if path is writable"""
    if not os.access(os.path.dirname(f) or ".", os.W_OK):
        raise PyseederException("Path is not writable: {}".format(f))
