from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-ffmpeg",
    version="1.0.0",
    description="CLI-Anything harness for FFmpeg — make ffmpeg agent-native",
    long_description=open("FFMPEG.md").read(),
    long_description_content_type="text/markdown",
    author="CLI-Anything Team",
    url="https://github.com/HKUDS/CLI-Anything",
    license="MIT",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-ffmpeg=cli_anything.ffmpeg.ffmpeg_cli:main",
        ],
    },
    package_data={
        "cli_anything.ffmpeg": ["skills/*.md"],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
)
