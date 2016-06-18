# -*- coding: utf-8 -*-
"""Installer for the bika.lims package."""

from setuptools import find_packages
from setuptools import setup

version = '4.0.dev0'

long_description = (
    open('README.rst').read() +
    '\n' +
    'Contributors\n' +
    '============\n' +
    '\n' +
    open('CONTRIBUTORS.rst').read() +
    '\n' +
    open('CHANGES.rst').read() +
    '\n')

setup(
    name='bika.lims',
    version=version,
    description="Bika open source laboratory information management system",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: "
        "GNU Affero General Public License v3 or later (AGPLv3+)",
    ],
    keywords='Python Plone',
    author='',
    author_email='support@bikalabs.com',
    url='https://pypi.python.org/pypi/bika.lims',
    license='AGPLv3+',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['bika'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.api',
        'z3c.jbot',
        'collective.z3cform.datagridfield',
        'plone.formwidget.autocomplete',
        'plone.principalsource',
        'z3c.relationfield',
        'plone.app.dexterity',
        # 'bika.magnitudefield',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
