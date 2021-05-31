from setuptools import find_packages
from setuptools import setup

setup(
    name='giat@hobbymarks',
    version='2021.05.31',
    packages=find_packages('.'),
    url='https://github.com/hobbymarks/giat',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    author='HobbyMarks',
    author_email='ihobbymarks@gmail.com',
    description='Change Local Git Repo Directory name to Git@Org Style',
    long_description='Change Local Git Repo Directory name to Git@Org Style',
    entry_points={
        'console_scripts': [
            'giat = giat:run_main',
        ],
    },
)
