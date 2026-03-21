from setuptools import setup, find_packages

setup(
    name="cli-anything-ps",
    version="1.0.0",
    description="CLI-Anything harness for ps",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-ps=cli_anything.ps.ps_cli:main",
        ],
    },
)
