#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='django-tastypie-extensions',
    version='0.0.1-alpha',
    description='A set of extended capabilities for django-tastypie',
    author='Jason Bartz',
    author_email='daniel@toastdriven.com',
    url='http://github.com/washingtonpost/django-tastypie-extensions/',
    # long_description=open('README.rst', 'r').read(),
    packages=[
        'tastypie_extensions',
    ],
    zip_safe=False,
    install_requires=[
        'django-tastypie',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
