from setuptools import setup, find_packages

setup(
    name="cli-anything-awk",
    version="1.0.0",
    description="CLI-Anything harness for awk",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-awk=cli_anything.awk.awk_cli:main",
        ],
    },
)
