#!/usr/bin/env python3

""" Setup script for packaging and installation. """

from distutils.core import setup

with open('README.rest', 'r', encoding='utf-8') as fin:
    LONG_DESCRIPTION = fin.read()

setup(
    #
    # Basic information
    #
    name='pinyin-dec',
    version='1.0.0',
    author='yaoguai',
    author_email='lapislazulitexts@gmail.com',
    url='https://github.com/yaoguai/pinyin-dec',
    license='MIT',
    #
    # Descriptions & classifiers
    #
    description='Decorate Pinyin text with its proper diacritics.',
    long_description=LONG_DESCRIPTION,
    keywords='hanyu pinyin chinese cjk asia language',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Religion',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'],
    #
    # Included Python files
    #
    scripts=['pinyin-dec'],
    py_modules=['pinyin_dec'],
    data_files=[
        ('share/doc/pinyin-dec', [
            'LICENSE.rest',
            'README.rest']),
        ('share/man/man1', [
            'pinyin-dec.1'])]
)
