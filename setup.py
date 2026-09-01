from setuptools import setup

setup(
   use_scm_version=True,
   setup_requires=['setuptools_scm'],
   name='alaska_io',
   author='Carsten Schubert',
   author_email='c.schubert@icm-chemnitz.de',
   packages=['alaska_io'],
   url='https://github.com/ICM-Chemnitz/alaska_io',
   license='LGPL-3.0',
   license_files = ('LICENSE',),
   description='Alaska IO Python Package',
   long_description=open('README.md').read(),
   install_requires=['numpy','h5py'],
)
