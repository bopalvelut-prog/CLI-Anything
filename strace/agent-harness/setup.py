from setuptools import setup, find_packages

setup(
    name="cli-anything-strace",
    version="1.0.0",
    description="CLI-Anything harness for strace",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-strace=cli_anything.strace.strace_cli:main",
        ],
    },
)
