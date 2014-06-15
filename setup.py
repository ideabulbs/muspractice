from setuptools import setup, find_packages
import sys, os

version = 'R0.0.1'

setup(name='muspractice',
      version=version,
      description="Music practice assistant based on spaced repetition method",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Andrei Matveyeu',
      author_email='andrei@ideabulbs.com',
      url='https://github.com/ideabulbs/muspractice',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
