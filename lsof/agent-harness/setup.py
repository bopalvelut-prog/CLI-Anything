from setuptools import setup, find_packages

setup(
    name="cli-anything-lsof",
    version="1.0.0",
    description="CLI-Anything harness for lsof",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-lsof=cli_anything.lsof.lsof_cli:main",
        ],
    },
)
