# -*- coding: utf-8 -*-
"""Grammer for EPICS database
"""

from pyparsing import *

# General

_annoated={}

def annotate(s,loc,toks):
    out=[]
    for t in toks:
        cls=_annoated.get(t.__class__)
        if cls is None:
            class Annotated(t.__class__):
                file=None
                lineno=None
                col=None
            _annoated[t.__class__]=Annotated
            cls=Annotated
        tt=cls(t)
        tt.lineno=lineno(loc,s)
        tt.col=col(loc,s)
        out.append(tt)
    return out

def listToDict(toks):
    return dict(toks.asList())

upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

fldname = upper + '0123456789'

UnQuotedString = Optional( CharsNotIn(' \t\r\n)') + 
                           ZeroOrMore( White(' \t') +
                                       CharsNotIn(' \t\r\n)')
                           )
                         ).setName("Un-quoted string")

DBValue = QuotedString('"', unquoteResults=True) | \
          Combine(UnQuotedString)
DBValue=DBValue.addParseAction(annotate)

Comment = pythonStyleComment

Include = Keyword("include").setResultsName('what') + \
          QuotedString('"').setResultsName('name')

#TODO: Don't work for CPP because Comment is applied
CCode = Literal("%").setParseAction(lambda _:'CCode').setResultsName('what') + \
        restOfLine.setResultsName('code')

# Menues

MenuHead = Keyword("menu").setResultsName('what') + \
                      Suppress("(") + \
                      Word(alphanums).setResultsName('name') + \
                      Suppress(")")

MenuEntry = Keyword("choice").suppress() + \
             Suppress("(") + \
		     Word(alphanums+'_') + \
		     Suppress(",") + \
		     QuotedString('"') + \
		     Suppress(")")
MenuEntry = Group(MenuEntry)

Menu = MenuHead + Suppress("{") + \
	      OneOrMore( MenuEntry ).setResultsName('choices').setParseAction(listToDict) + \
	      Suppress("}")

# Records

RecordHead = Keyword("recordtype").setResultsName('what') + \
                      Suppress("(") + \
                      Word(alphanums).setResultsName('name') + \
                      Suppress(")")
RecordHead.setName("Record header")

# Record body statements

RecordFieldHead = Keyword("field").setResultsName('what') + Suppress("(") + \
                  Word(fldname).setResultsName('name') + Suppress(",") + \
                  Word(upper+'_').setResultsName('dbf') + Suppress(")")

_valQuoted = ['prompt', 'initial', 'extra']
_valPlain = ['asl','promptgroup','special','pp',
             'interest','base','size','menu']

_fieldAttrs=[]
for v in _valQuoted:
    a=Keyword(v) + Suppress("(") + QuotedString('"') + Suppress(")")
    _fieldAttrs.append(a)

for v in _valPlain:
    a=Keyword(v) + Suppress("(") + Word(alphanums+'_') + Suppress(")")
    _fieldAttrs.append(a)

RecordFieldAttr = reduce(lambda a,b:a|b, _fieldAttrs)

RecordField = RecordFieldHead + Suppress("{") + \
          OneOrMore( Group(RecordFieldAttr) ).setParseAction(listToDict).setResultsName('attrs') + \
          Suppress("}")

RecordEntry = Group( RecordField | Include | CCode )

Record = RecordHead + Suppress("{") + \
          Group( OneOrMore( RecordEntry ) ).setResultsName('fields') + \
          Suppress("}")

# Record Instances

InstHead = Keyword("record").setResultsName('what') + Suppress("(") + \
                  Word(alphanums).setResultsName('rec') + Suppress(",") + \
                  DBValue.setResultsName('name') + Suppress(")")

InstField = Keyword("field").setResultsName('what') + Suppress("(") + \
                  Word(fldname).setResultsName('name') + Suppress(",") + \
                  DBValue.setResultsName('value') + Suppress(")")

InstInfo = Keyword("info").setResultsName('what') + Suppress("(") + \
                  Word(alphanums+'_').setResultsName('name') + Suppress(",") + \
                  QuotedString('"').setResultsName('value') + Suppress(")")

InstAlias = Keyword("alias").setResultsName('what') + Suppress("(") + \
                  QuotedString('"').setResultsName('name') + Suppress(")")

InstEntry = Group( InstField | InstInfo | InstAlias | Include )

Inst = InstHead + Suppress("{") + \
          Group( ZeroOrMore( InstEntry ) ).setResultsName('fields') + \
          Suppress("}")

# misc

Registrar = Keyword('registrar') + Suppress("(") + \
            Word(alphanums+'_').setResultsName('name') + Suppress(")")

Variable = Keyword("variable").setResultsName('what') + Suppress("(") + \
           Word(alphanums+'_').setResultsName('name') + Suppress(",") + \
           Word(alphanums+'_').setResultsName('ctype') + Suppress(")")

Device = Keyword("device").setResultsName('what') + Suppress("(") + \
         Word(alphanums+'_').setResultsName('rec') + Suppress(",") + \
         Word(upper+'_').setResultsName('link') + Suppress(",") + \
         Word(alphanums+'_').setResultsName('name') + Suppress(",") + \
         QuotedString('"').setResultsName('dtyp') + Suppress(")")

# Root nodes

DBD = OneOrMore( Group(Record   | Menu   | Inst  | Registrar | \
                       Variable | Device | CCode | Include) )
DBD.ignore(Comment)

# include from recordtype
RecordInclude = OneOrMore( RecordEntry )
RecordInclude.ignore(Comment)

# include from recordtype
InstInclude = OneOrMore( InstEntry )
InstInclude.ignore(Comment)
