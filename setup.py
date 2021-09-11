from distutils.core import setup
import pathlib
import pkg_resources
import os
from setuptools import find_packages

with pathlib.Path("requirements.txt").open() as requirements_txt:
    install_requires = [str(requirement) for requirement in pkg_resources.parse_requirements(requirements_txt)]

setup(
    name="foreverbull",
    version="0.0.7",
    description="Core Python functionality for Foreverbull",
    author="Henrik Nilsson",
    author_email="henrik@lhjnilsson.com",
    packages=find_packages("."),
    install_requires=install_requires,
)
