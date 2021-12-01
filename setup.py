from setuptools import setup

setup(
    name="Examples",
    version="0.0.1",
    description="Examples in Robot Framework. Expands example data to individual test cases",
    packages=['.'],
    python_requires='>=3.8',
    install_requires=['robotframework', 'RoboPandas']
)
