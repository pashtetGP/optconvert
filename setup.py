from setuptools import setup, find_packages
import os

INSTALL_REQUIRES = []
#INSTALL_REQUIRES.append('oauth2')

license='MIT'
if os.path.exists('LICENSE'):
  license = open('LICENSE').read()

long_description = """
    The Splitwise SDK provides Splitwise APIs to get data from your Splitwise Account.
    https://github.com/pashtetgp/opt_convert - README
  """

setup(name='opt_convert',
      version='0.0.1',
      description='Converter of ',
      long_description=long_description,
      author='Pavlo Glushko',
      author_email='pavloglushko@gmail.com',
      url='https://github.com/pashtetgp/opt_convert',
      download_url='https://github.com/pashtetgp/opt_convert/tarball/0.0.1',
      license=license,
      packages=find_packages(),
      classifiers=[
        'Intended Audience :: Scientists',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Libraries :: Python Modules'
        ],
        install_requires=INSTALL_REQUIRES
)