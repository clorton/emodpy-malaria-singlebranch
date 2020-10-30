import setuptools
from setuptools.extension import Extension
import version

with open("README.md", "r") as fh:
    long_description = fh.read()
    ext_name = "emodpy_malaria"

setuptools.setup(
    name=ext_name,
    version=version.__version__,
    author="Jonathan Bloedow",
    author_email="jbloedow@idmod.org",
    description="IDM's malaria-specific EMOD API support scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/InstituteforDiseaseModeling/emodpy-covid",
    packages=setuptools.find_packages(),
    include_package_data=True,
    setup_requires=['wheel'],
    install_requires=['emod_api'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
