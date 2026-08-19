from setuptools import setup

setup(
   name='alaska_io',
   version='0.1.3',
   author='Carsten Schubert',
   author_email='c.schubert@icm-chemnitz.de',
   packages=['alaska_io'],
   url='',
   license='CC-BY-NC-4.0 License',
   description='Alaska IO Python Package',
   long_description=open('README.md').read(),
   install_requires=['numpy','h5py'],
)
