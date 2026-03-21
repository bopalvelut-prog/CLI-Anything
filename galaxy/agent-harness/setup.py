from setuptools import setup, find_packages

setup(
    name="cli-anything-galaxy",
    version="1.0.0",
    description="CLI-Anything harness for galaxy",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-galaxy=cli_anything.galaxy.galaxy_cli:main",
        ],
    },
)
