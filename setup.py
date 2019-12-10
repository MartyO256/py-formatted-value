import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read().strip()

setuptools.setup(
    name="fvalue",
    version="1.0.0",
    author="Marc-Antoine Ouimet",
    author_email="ouimetmarcantoine@gmail.com",
    description=(
        "Values and their uncertainties formatter up to a given "
        "number of significant figures in the uncertainty."
    ),
    long_description=long_description,
    long_descript_content_type="text/markdown",
    url="https://github.com/MartyO256/py-formatted-value",
    packages=setuptools.find_packages(),
    keywords="significant figures values uncertainty formatting format",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ]
)
