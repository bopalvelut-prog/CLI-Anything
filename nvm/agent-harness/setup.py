from setuptools import setup, find_packages

setup(
    name="cli-anything-nvm",
    version="1.0.0",
    description="CLI-Anything harness for nvm",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-nvm=cli_anything.nvm.nvm_cli:main",
        ],
    },
)
