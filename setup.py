#!/usr/bin/env python
# This file is part of the vecnet.azure package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/vecnet.azure
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Note that vecnet is a namespace package.
# Please refer to https://pythonhosted.org/setuptools/setuptools.html#namespace-packages for additional details
#
# This implies that __init__.py in vecnet package MUST contain the line
# __import__('pkg_resources').declare_namespace(__name__)
# This code ensures that the namespace package machinery is operating and the current package is registered
# as a namespace package. You must NOT include any other code and data in a namespace packages's __init__.py

from setuptools import setup, find_packages

setup(
    name="vecnet.azure",
    version="0.0.1",
    license="MPL 2.0",
    author="Natalie Sanders",
    author_email="nsanders0702@gmail.com",
    description="Azure library for VecNet-CI project.",
    keywords="azure windows emod openmalaria",
    url="https://github.com/vecnet/vecnet.azure",
    packages=find_packages(),  # https://pythonhosted.org/setuptools/setuptools.html#using-find-packages
    namespace_packages=['vecnet', ],
    scripts=['bin/om_expand.cmd', 'bin/om_expand'],
    install_requires=["azure", ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
