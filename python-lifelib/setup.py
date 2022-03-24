from setuptools import setup, find_packages
import lifelib

lifelib.reset_tree()

import os
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'lifelib', 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='python-lifelib',
    version=lifelib.__version__,
    description='Algorithms for manipulating and simulating patterns in cellular automata',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Adam P. Goucher',
    author_email='adam@hatsya.com',
    url='https://gitlab.com/apgoucher/lifelib',
    license='MIT',
    packages=['lifelib'],
    test_suite='lifelib.tests',
    include_package_data=True,
    zip_safe=False,
    install_requires=['numpy>=1.13', 'tqdm>=4.27'],
    extras_require={'notebook': ['jupyter']},
    classifiers = [
        'Development Status :: 4 - Beta',

        # MIT licence as always:
        'License :: OSI Approved :: MIT License',

        # Since we require gcc or clang to compile:
        'Operating System :: POSIX',
        'Programming Language :: C++',
        'Programming Language :: Assembly',

        # Lifelib is compatible with Python 2 and 3, and has been tested on:
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        # Cellular automata fall into these categories:
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Life',
        'Topic :: Scientific/Engineering :: Mathematics',
    ])
