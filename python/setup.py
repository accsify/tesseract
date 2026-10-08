from setuptools import setup, find_packages

setup(
    name="accsify-tesseract",
    version="5.5.0.1",
    author="accsify",
    description="Official Python Wrapper for Accsify Monolithic Tesseract OCR Engine",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "accsify-tesseract=accsify_tesseract.cli:main",
        ],
    },
)
