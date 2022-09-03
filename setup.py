from distutils.core import setup
from os import path
from codecs import open
import sys
import os

version = '0.1'

here = path.abspath(path.dirname(__file__))

with open("README.md", "r", "utf-8") as f:
    readme = f.read()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

setup(
    name="bloryc",
    version=version,
    description="Bloryc SDK API",
    license="MIT",
    author="Standard Sats",
    long_description=readme,
    maintainer="Ilya Evdokimov",
    packages=["bloryc"],
    keywords="sdk bloryc",
    package_data={
        "": [
            "LICENSE",
        ]
    },
    install_requires=["requests>2.4.0", "future", "six"],
    test_suite="nose.collector",
    tests_require=["nose"],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
)
