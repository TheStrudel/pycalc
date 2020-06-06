from setuptools import setup, find_packages


setup(
    name='pycalc',
    description='pure command-line calculator',
    version='',
    author='Alex',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['pycalc = calculator.pycalc:main']
    }
)
