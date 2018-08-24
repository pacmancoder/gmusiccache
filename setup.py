from setuptools import setup

setup(name='gmusiccache',
      version='0.1',
      description='Caches your favourite music locally',
      license='GLWTS',
      packages=['gmusiccache'],
      install_requires=['gmusicapi', 'eyed3'],
      zip_safe=False)