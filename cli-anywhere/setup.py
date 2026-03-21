from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-anything",
    version="1.0.0",
    author="CLI-Anything contributors",
    author_email="",
    description="Turn any software into an AI-controllable tool — 645+ CLI harnesses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    extras_require={
        "langchain": ["langchain>=0.1.0"],
        "crewai": ["crewai>=0.1.0"],
        "mcp": ["mcp>=1.0.0"],
        "all": ["langchain>=0.1.0", "crewai>=0.1.0", "mcp>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything=cli_anything.cli_anything:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
