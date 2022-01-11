#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 - 2021 Pionix GmbH and Contributors to EVerest
#
"""Everest Dependency Manager
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='edm_tool',
    version='0.1.3',
    description='A simple dependency manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/EVerest/everest-dev-environment',
    author='Kai-Uwe Hermann',
    author_email='kai-uwe.hermann@pionix.de',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    install_requires=['Jinja2>=2.11',
                      'PyYAML>=5.3'],
    package_data={
        'edm_tool': ['templates/cpm.jinja', 'cmake/CPM.cmake', 'cmake/EDMConfig.cmake', 'edm-completion.bash'],
    },
    entry_points={
        'console_scripts': [
            'edm=edm_tool:main',
        ],
    },
)
