from setuptools import setup

"""
1. set "HOME=E:/code/sqlalchemy-mixins"
2. python setup.py sdist upload -r testpypi
   or
   python setup.py sdist upload -r pypi

see http://peterdowns.com/posts/first-time-with-pypi.html
"""

def requirements():
    import os
    filename = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    return [line.rstrip('\n') for line in open(filename).readlines()]

setup(name='sqlalchemy_mixins_for_starlette',
      version='1.0',
      description='Active Record, Django-like queries, nested eager load '
                  'and beauty __repr__ for SQLAlchemy',
      url='https://github.com/scil/sqlalchemy-mixins-for-starlette',
      download_url = 'https://github.com/scil/sqlalchemy-mixins-for-starlette/archive/master.tar.gz',
      author='Alexander Litvinenko',
      author_email='litvinenko1706@gmail.com',
      license='MIT',
      packages=['sqlalchemy_mixins'],
      zip_safe=False,
      include_package_data=True,
      install_requires=[
          "SQLAlchemy >= 1.0",
          "six",
          "typing; python_version >= '3.7'"
      ],
      keywords=['sqlalchemy', 'active record', 'activerecord', 'orm',
                'django-like', 'django', 'eager load', 'eagerload',  'repr',
                '__repr__', 'mysql', 'postgresql', 'pymysql', 'sqlite'],
      platforms='any',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Database',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover'],
  )
