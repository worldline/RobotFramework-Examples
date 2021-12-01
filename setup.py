from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="RobotFramework-Examples",
    version="0.0.3",
    author="Vernon Crabtree",
    author_email="vernon.b.crabtree@gmail.com",
    description="Examples in Robot Framework. Expands example data to individual test cases",
    long_description=long_description,
    packages=['.'],
    python_requires='>=3.8',
    project_urls={
        "Examples": "https://github.com/worldline/RobotFramework-Examples",
    },    
    install_requires=['robotframework', 'pandas', 'sqlalchemy']
)
