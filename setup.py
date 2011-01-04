#!/usr/bin/env python

from distutils.core import setup

setup(name='pyPDB', 
          version='0.1', 
          description="Utilities for working with EPICS PDB files", 
          author='Michael Davidsaver', 
          author_email='mdavidsaver@bnl.gov', 
          packages=['pyPDB',
                    'pyPDB.dbd',
                    'pyPDB.dbd.test',
                    'pyPDB.po',
                   ], 
          scripts=['getpvs',  'applypvs'], 
          requires=
            ['pyparsing (>=1.5.5)'],
      )
