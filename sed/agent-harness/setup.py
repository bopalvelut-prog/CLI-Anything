from setuptools import setup, find_packages

setup(
    name="cli-anything-sed",
    version="1.0.0",
    description="CLI-Anything harness for sed",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-sed=cli_anything.sed.sed_cli:main",
        ],
    },
)
