from setuptools import setup, find_packages

setup(
    name="cli-anything-find",
    version="1.0.0",
    description="CLI-Anything harness for find",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-find=cli_anything.find.find_cli:main",
        ],
    },
)
