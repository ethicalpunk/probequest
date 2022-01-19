#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os

if os.geteuid() != 0:
    print("You need root privileges to execute the installation!")
    sys.exit()

try:
    subprocess.call(["airmon-ng"])
except FileNotFoundError:
    print("Installing aircrack-ng.......\n")
    subprocess.run(["apt", "install", "aircrack-ng", "-y"])

subprocess.call(["mkdir", "/usr/local/bin/probequestdata"])
subprocess.call(["mkdir", "/usr/local/bin/probequestdata/config"])

idir = os.popen("pwd").read().strip("\n")
insdir = open(f"/usr/local/bin/probequestdata/config/installdirectory.dnt", "w+"); insdir.write(idir); insdir.close()

try:
    from setuptools import setup, find_packages
except Exception as setuptools_not_present:
    raise ImportError(
        "Setuptools is required to install ProbeQuest!"
    ) from setuptools_not_present

from codecs import open as fopen
from os.path import dirname, abspath, join

DIR = dirname(abspath(__file__))

VERSION = "0.7.2"

with fopen(join(DIR, "README.rst"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="probequest",
    version=VERSION,
    description="Toolkit for Playing with Wi-Fi Probe Requests",
    long_description=LONG_DESCRIPTION,
    license="GPLv3",
    keywords="wifi wireless security sniffer",
    project_urls={
        "Documentation": "https://probequest.readthedocs.io",
        "Source Code": "https://github.com/SkypLabs/probequest",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "probequest = probequest.cli:main",
        ]
    },
    python_requires=">=3.6, <4",
    install_requires=[
        "netaddr >= 0.7.19",
        "scapy >= 2.4.3",
    ],
    extras_require={
        "complete": [
            "faker_wifi_essid",
        ],
        "tests": [
            "flake8",
            "pylint",
            "tox"
        ],
        "docs": [
            "sphinx >= 3.2.0",
            "sphinxcontrib-seqdiag >= 2.0.0",
            "sphinx-argparse >= 0.2.2",
            "sphinx_rtd_theme >= 0.5.0",
        ],
    },
)
