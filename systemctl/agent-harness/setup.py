from setuptools import setup, find_packages

setup(
    name="cli-anything-systemctl",
    version="1.0.0",
    description="CLI-Anything harness for systemctl",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-systemctl=cli_anything.systemctl.systemctl_cli:main",
        ],
    },
)
