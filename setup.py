from setuptools import setup

setup(
    name="RobotFramework-Examples",
    version="0.0.1",
    author="Vernon Crabtree",
    author_email="vernon.b.crabtree@gmail.com",
    description="Examples in Robot Framework. Expands example data to individual test cases",
    packages=['.'],
    python_requires='>=3.8',
    project_urls={
        "Examples": "https://github.com/worldline/RobotFramework-Examples",
    },    
    install_requires=['robotframework', 'pandas', 'sqlalchemy']
)
