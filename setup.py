from setuptools import setup, find_packages
import os

INSTALL_REQUIRES = []
INSTALL_REQUIRES.append('scipy') # for mplpy
INSTALL_REQUIRES.append('matplotlib') # for mplpy
INSTALL_REQUIRES.append('wxPython') # for mplpy
INSTALL_REQUIRES.append('mplpy') # for optconvert
INSTALL_REQUIRES.append('mplpy')

version = '0.0.1'

license='MIT'
if os.path.exists('LICENSE'):
  license = open('LICENSE').read()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='optconvert',
      version=version,
      python_requires='>=3.6', # does not work for some reason
      description='Converter for mathematical optimization formats: .mpl, .lp, .xa, .sim, .mpl, .gms, .mod, .xml, .mat.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      keywords='converter mathematical optimization mps',
      author='Pavlo Glushko',
      author_email='pavloglushko@gmail.com',
      url='https://github.com/pashtetgp/optconvert',
      download_url=f'https://github.com/pashtetGP/optconvert/archive/{version}.tar.gz',
      license=license,
      packages=find_packages(),
      classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
      include_package_data=True, # files from MANIFEST.in
      test_suite='tests',
      entry_points = {
        'console_scripts': ['optconvert=optconvert.command_line:command_line'],
      },
      install_requires=INSTALL_REQUIRES
)