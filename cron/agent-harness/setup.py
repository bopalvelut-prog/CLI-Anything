from setuptools import setup, find_packages

setup(
    name="cli-anything-cron",
    version="1.0.0",
    description="CLI-Anything harness for cron",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "cli-anything-cron=cli_anything.cron.cron_cli:main",
        ],
    },
)
