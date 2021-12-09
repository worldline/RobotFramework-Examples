from setuptools import setup

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

CLASSIFIERS = '''
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3 :: Only
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
'''.strip().splitlines()

setup(
    name="RobotFramework-Examples",
    version="0.1.1",
    author="Vernon Crabtree",
    author_email="vernon.b.crabtree@gmail.com",
    description="Examples in Robot Framework. Expands example data to individual test cases",
    long_description=long_description,
    license='Apache License 2.0',
    keywords='robotframework testing testautomation bdd gwen examples',
    platforms='any',
    classifiers=CLASSIFIERS,
    packages=['.'],
    python_requires='>=3.8',
    project_urls={
        "Examples": "https://github.com/worldline/RobotFramework-Examples",
    },    
    install_requires=['robotframework', 'pandas', 'sqlalchemy', 'docutils']
)
