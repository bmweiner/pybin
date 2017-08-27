import os
import shutil
from setuptools import setup

__name__ = 'pybin'
__version__ = '0.1'
__description__ = 'Getting Things Done with Python.'

# setup package scripts
pkg = os.path.dirname(os.path.realpath(__file__))
script_dir = os.path.join(pkg, 'scripts')

try:
  shutil.rmtree(script_dir)
except OSError:
  pass

os.makedirs(script_dir)

fnames = os.listdir(os.path.join(pkg, __name__))
fnames = [f for f in fnames if f.endswith('.py') and not f.startswith('_')]
scripts = []

content = '#!/usr/bin/env bash\n\npython -m {}.{} "$@"'

for fname in fnames:
  module = fname[:-3]
  script = os.path.join('scripts', module)
  scripts.append(script)
  with open(os.path.join(pkg, script), 'w') as f:
    f.write(content.format(__name__, module))

setup(name=__name__,
      version=__version__,
      author='bmweiner',
      author_email='bmweiner@users.noreply.github.com',
      url='https://github.com/bmweiner/pybin',
      description=__description__,
      license='MIT License',
      packages=[],
      include_package_data=True,
      scripts=scripts,
      install_requires=[])

print('Scripts Installed: {}'.format(scripts))
