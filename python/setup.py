#!/usr/bin/env python3
"""
Setup script for accsify-tesseract Python package.
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

from setuptools import setup, find_packages

setup(
    name="accsify-tesseract",
    version="5.5.0.1",
    author="accsify",
    author_email="contact@accsify.com",
    description="Official Python SDK and CLI for the Accsify Monolithic Tesseract OCR Engine",
    packages=find_packages(),
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "accsify_tesseract": ["py.typed"],
    },
    entry_points={
        "console_scripts": [
            "accsify-tesseract=accsify_tesseract.cli:main",
        ],
    },
)
