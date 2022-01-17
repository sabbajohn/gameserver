from setuptools import setup

setup(name='webingo',
      version='0.1',
      description='Best casino game server in the whole world',
      url='https://bitbucket.org/amazoniagames/amz-gameserver/src/master/',
      author='Lucas Camargo',
      author_email='lucas@camargo.eng.br',
      license='Proprietary',
      packages=['webingo'],
      install_requires=[
          'redis',
          'tornado',
          'pycurl',
          'numpy'
      ],
      zip_safe=False) 
