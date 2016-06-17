from setuptools import setup, find_packages
import os

version = '4.0.dev0'

setup(name='bika.lims',
      version=version,
      description="Bika Open Source Laboratory Information Management System",
      long_description=open("README.md").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Open Source Laboratory Information Management System',
      url='http://www.bikalims.org',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bika'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.api',
          'collective.z3cform.datagridfield',
          'magnitude',
          'plone.formwidget.autocomplete',
          'plone.principalsource',
          'z3c.relationfield',
      ],
      extras_require={
          'test': [
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
