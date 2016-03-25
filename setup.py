# -*- coding: utf-8 -*-
"""REST ORM.

An ORM adapter for RESTful endpoints.
"""
from setuptools import find_packages, setup


setup(
    name='rest-orm',
    version='0.1',
    url='https://github.com/caxiam/model-api',
    license='MIT',
    author='Colton Allen',
    author_email='colton.allen@caxiam.com',
    description='An ORM for RESTful endpoints.',
    long_description=__doc__,
    packages=find_packages(exclude=("test*", )),
    package_dir={'rest_orm': 'rest_orm'},
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='tests'
)
