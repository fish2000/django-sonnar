#/usr/bin/env python
#from distutils.core import setup, Extension

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import sys, os
import sonnar

if 'publish' in sys.argv:
    os.system('python setup.py sdist upload')
    sys.exit()

tests_require = ['nose', 'django-nose']

setup(
    name=sonnar.__title__,
    version='%s.%s.%s' % sonnar.__version__,
    description='Modular image processing for your Django apps.',
    author=sonnar.__author__,
    author_email=sonnar.__email__,
    maintainer=sonnar.__author__,
    maintainer_email=sonnar.__email__,
    license=sonnar.__license__,
    url=sonnar.__url__,
    
    test_suite='tests.core.tests',
    install_requires=[
        'setuptools',
        'django-signalqueue>=0.2.8',
        'django-delegate>=0.1.8',
    ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    }
    packages=[
        'sonnar',
        'tests',
        'tests.core',
    ],
    package_data={
    },
    
    keywords=[
        'django',
        'image',
        'images',
        'processing',
        'modular',
        'features',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ]
)
