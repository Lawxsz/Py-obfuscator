"""
Setup script for Python Code Obfuscator
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    """Read a file and return its contents."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename), encoding='utf-8') as f:
        return f.read()

setup(
    name="py-obfuscator",
    version="1.0.0",
    author="Blank-C and Lawxsz",
    author_email="",
    description="Multi-layer Python code obfuscator for source code protection",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/Lawxsz/Py-obfuscator",
    py_modules=["obf"],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    entry_points={
        "console_scripts": [
            "pyobf=obf:main",
        ],
    },
    keywords="obfuscator obfuscation code-protection python security",
    project_urls={
        "Bug Reports": "https://github.com/Lawxsz/Py-obfuscator/issues",
        "Source": "https://github.com/Lawxsz/Py-obfuscator",
    },
)
