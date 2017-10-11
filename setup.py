import sys
sys.path.pop(0)
from setuptools import setup

setup(
    name="micropython-ili934x",
    py_modules=["ili934x"],
    version="0.1.0",
    description="MicroPython SPI driver for ILI934X based displays",
    long_description="",
    keywords="micropython tft lcd",
    url="https://github.com/tuupola/micropython-ili934x",
    author="Mika Tuupola",
    author_email="tuupola@appelsiini.net",
    maintainer="Mika Tuupola",
    maintainer_email="tuupola@appelsiini.net",
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: Implementation :: MicroPython",
        "License :: OSI Approved :: MIT License",
    ],
)
