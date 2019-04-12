import setuptools
import targetdecoy

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="targetdecoy",
    version=targetdecoy.__version__,
    author="William E Fondrie",
    author_email="fondriew@gmail.com",
    description="Proteomics confidence estimation using target-decoy competition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wfondrie/targetdecoy",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
