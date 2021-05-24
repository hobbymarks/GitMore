from setuptools import find_packages
from setuptools import setup

setup(
    name='giat@hobbymarks',
    version='2021.05',
    packages=find_packages('.'),
    url='https://github.com/hobbymarks/giat',
    license='MIT',
    author='HobbyMarks',
    author_email='ihobbymarks@gmail.com',
    description='Change Local Git Repo Directory name to Git@Org Style',
    entry_points={
        'console_scripts': [
            'giat = giat:main',
        ],
    },
)
