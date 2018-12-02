import os
from setuptools import setup, Command

def readme():
    with open('README.rst') as f:
        return f.read()

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf build dist *.pyc *.tgz *.egg-info')


setup(name = 'pirata_codex',
      version = '0.1',
      description = 'Code for Reddit Pirates Clashing',
      long_description = readme(),
      author = 'Katie Harrington',
      author_email = 'katie.megan.harrington@gmail.com',
      license = 'MIT',
      packages = ['pirata_codex'],
      package_dir = {'pirata_codex':'python'},
      cmdclass={'clean':CleanCommand,},
      scripts = ['bin/alive_check.py',
                 'bin/update_tables.py' ]
      )



