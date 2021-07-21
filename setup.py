import sys

from setuptools import setup, find_packages

if sys.version_info < (3,6):
    sys.exit("This program requires python 3.6 or above.")

REQUIREMENTS=['click>=8.0.0']
if sys.platform.startswith("win"): REQUIREMENTS.append('windows-curses>=2.0.0')

setup(
    name='nai-cli',
    version='0.1.0',
    description='A terminal-based NovelAI client',
    keywords=['cli', 'novelai'],
    author='dagal',
    url='',
    packages=find_packages(include=['naicli']),
    install_requires=REQUIREMENTS,
    entry_points={'console_scripts': ['nai-cli = naicli.main:main']},
    tests_require=['pytest', 'hypothesis', 'pyte']
)