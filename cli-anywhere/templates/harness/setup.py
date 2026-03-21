from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-{{APP_NAME}}",
    version="1.0.0",
    author="cli-anything contributors",
    description="{{APP_NAME}} CLI harness for agent-native operations",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    python_requires=">=3.10",
    install_requires=["click>=8.0.0", "prompt-toolkit>=3.0.0"],
    entry_points={
        "console_scripts": [
            "cli-anything-{{APP_NAME}}=cli_anything.{{APP_NAME}}.{{APP_NAME}}_cli:main",
        ],
    },
    package_data={"cli_anything.{{APP_NAME}}": ["skills/*.md"]},
    include_package_data=True,
    zip_safe=False,
)
