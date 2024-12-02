import sys
from pathlib import Path

from setuptools import find_packages, setup

DIRECTORY_PATH = Path(__file__).parent
README = (DIRECTORY_PATH / "README.md").read_text()

VERSION = "0.4.0"
INSTALL_REQUIRES = ["py-sc-client>=0.4.0"]
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 8)


if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        # pylint: disable=consider-using-f-string
        """
            ==========================
            Unsupported Python version
            ==========================
            This version of py-sc-client requires at least Python {}.{}, but
            you're trying to install it on Python {}.{}. To resolve this,
            consider upgrading to a supported Python version.
            """.format(
            *REQUIRED_PYTHON, *CURRENT_PYTHON
        )
    )
    sys.exit(1)


setup(
    name="py-sc-kpm",
    version=VERSION,
    description="The Python implementation of the knowledge processing module for knowledge manipulations",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ostis-ai/py-sc-kpm",
    author="ostis-ai",
    license="MIT",
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="sc-kpm, kpm, knowledge processing",
    packages=find_packages(where="src", exclude=("tests",)),
    package_dir={"": "src"},
    python_requires=">=3.8, <4",
    install_requires=INSTALL_REQUIRES,
    project_urls={
        "Bug Reports": "https://github.com/ostis-ai/py-sc-kpm/issues",
        "Source": "https://github.com/ostis-ai/py-sc-kpm",
    },
)
