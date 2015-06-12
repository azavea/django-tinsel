from setuptools import setup, find_packages

author = 'Michael Maurizi'
author_email = 'info@azavea.com'

setup(
    name='django-tinsel',
    version='0.1.1',
    description='A python module for decorating function-based Django views',
    long_description=open('README.rst').read(),
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    url='http://github.com/azavea/django-tinsel',
    packages=find_packages(exclude=('test_app',)),
    license='Apache License (2.0)',
    keywords="django view decorator",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Environment :: Plugins",
        "Framework :: Django",
        "License :: OSI Approved :: Apache Software License"
    ],
    install_requires=['django>=1.5'],
)
