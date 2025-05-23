# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later

"""A benchmark based on MINLPLib instances and CAMINO solvers."""

from setuptools import setup, find_packages

setup(
    name="camino-benchmark",
    version="0.0.1",
    description="Benchmark solvers in CAMINO using MINLPLib test problems.",
    # url="https://github.com/minlp-toolbox/CAMINO-benchmark",
    author="Andrea Ghezzi, Wim Van Roy",
    author_email="andrea.ghezzi@imtek.uni-freiburg.de, wim.vr@hotmail.com",
    license="GPL-3.0",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    install_requires=[
        "caminopy>=0.1.2",
        "lxml>=5.4.0",
    ],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ]
)