from safestring import SafeString
from MySQLdb import *     # "inherit" from the module by importing everything
import MySQLdb
import sqlparse

class InjectionError(MySQLdb.ProgrammingError):
    """ Exception raised when SQL injection is caught """

def is_delim_pair(a, b):
    delims = [('"', '"'), ("'", "'"), ('(', ')'), ('[', ']'), ('{', '}')]
    return (a, b) in delims

def trim_delimiters(string):
    if len(string) > 1 and is_delim_pair(string[0], string[-1]):
        return string[1:-1]
    else:
        return string

def same_token(a, b):
    a = str(a)
    b = str(b)
    return a == b or trim_delimiters(a) == trim_delimiters(b)

def remove_safe_strings(inputs, tokens):
    """ Removes the inputs that correspond to specific tokens.  It is assumed
        inputs and tokens are in the same order, so they can be walked down in
        parallel.  Hence, if an input doesn't match, then no inputs after it
        will be searched.
        args:
            inputs (array of strings)
            tokens (array of sqlparse.sql.Tokens)
        returns: (array of strings) the input array with matches removed.
    """
    for t in tokens:
        if len(inputs) == 0:
            break
        current = str(inputs[0])
        if same_token(t, current):
            inputs = inputs[1:]     # inputs[0] is a token or subtree, is safe
        try:
            inputs = remove_safe_strings(inputs, t.tokens)
        except:
            pass   # if no tokens attribute, t is terminal
    return inputs


def queries_are_safe(query):
    """ Given a query, determines if it is safe.
        We assume raw strings are safe (ie. they came from the programmer).
        If input is a SafeString, we compare the unsafe substrings with the
        tokens generated from parsing the query.
    """
    if not isinstance(query, SafeString):
        return True
    parsed = sqlparse.parse(str(query))
    unsafe_strings = query.unsafe_substrings()
    for statement in parsed:
        unsafe_strings = remove_safe_strings(unsafe_strings, statement.tokens)
    return len(unsafe_strings) == 0


def connect(*args, **kwargs):
    db = MySQLdb.connect(*args, **kwargs)
    orig_cursor = db.cursor
    def cursor(*args, **kwargs):
        crsr = orig_cursor(*args, **kwargs)
        orig_execute = crsr.execute
        def execute(*args, **kwargs):
            if not queries_are_safe(args[0]):
                raise InjectionError()
            args = list(args)
            args[0] = str(args[0])
            return orig_execute(*args, **kwargs)
        crsr.execute = execute
        return crsr
    db.cursor = cursor
    return db
