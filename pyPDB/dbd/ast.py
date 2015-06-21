# -*- coding: utf-8 -*-

import re

class DBSyntaxError(RuntimeError):
    def __init__(self, msg, fname=None, lineno=None):
        RuntimeError.__init__(self, msg)
        self.fname, self.lineno = fname, lineno
    def __repr__(self):
        return 'DBSyntaxError %s:%d : %s'%(self.fname, self.lineno, self.message)
    __str__ = __repr__

_unquote = {
    'n':'\n',
    'r':'\r',
    't':'\t',
}

_quote = dict([(V, '\\'+K) for K,V in _unquote.items()])
_quote.update({
    '"': '\"',
})

_quotes = r'[\r\n\t]'

def _unescape(M):
    c = M.string[1]
    return _unquote.get(c,c)

def unescape(S):
    return re.sub(r'\\.', _unescape, S)

def _escape(M):
    c = M.string[0]
    return _quote.get(c,c)

def quote(S):
    return '"%s"'%re.sub(_quotes, _escape, S)

class Comment(object):
    def __init__(self, val, lineno=None):
        self.fname = None
        self.value, self.lineno = val, lineno
    def __repr__(self):
        return 'Comment("%s")'%self.value[:20]

class Code(object):
    def __init__(self, val, lineno=None):
        self.fname = None
        self.value, self.lineno = val, lineno
    def __repr__(self):
        return 'Code("%s")'%self.value[:20]

class Block(object):
    __slots__ = ('fname', 'lineno', 'name', 'args', 'argsquoted', 'body')
    def __init__(self, name, argval, argq, body=None, lineno=None):
        self.fname = None
        self.lineno = lineno
        self.name, self.args, self.body = name, argval, body
        self.argsquoted = argq

    def __repr__(self):
        return 'Block(%s, %s, %s)'%(self.name, self.args, self.body)
    __str__ = __repr__

class Command(object):
    __slots__ = ('fname', 'lineno', 'name', 'arg', 'argquoted')
    def __init__(self, name, argval, argq, lineno=None):
        self.fname = None
        self.lineno = lineno
        self.name, self.arg = name, argval
        self.argquoted = argq

    def __repr__(self):
        return 'Command(%s, %s)'%(self.name, self.arg)
    __str__ = __repr__