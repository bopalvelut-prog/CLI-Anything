from setuptools import setup, find_packages

setup(
    name="cli-anything-screen",
    version="1.0.0",
    description="CLI-Anything harness for screen",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-screen=cli_anything.screen.screen_cli:main",
        ],
    },
)
