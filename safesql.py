from safestring import SafeString
from MySQLdb import *
import MySQLdb
import logging

def connect(*args, **kwargs):
    db = MySQLdb.connect(*args, **kwargs)
    orig_cursor = db.cursor
    def cursor(*args, **kwargs):
        crsr = orig_cursor(*args, **kwargs)
        orig_execute = crsr.execute
        def execute(*args, **kwargs):
            if len(args) > 0 and isinstance(args[0], SafeString):
                args = list(args)
                # verify....
                args[0] = str(args[0])
            return orig_execute(*args, **kwargs)
        crsr.execute = execute
        return crsr
    db.cursor = cursor
    return db