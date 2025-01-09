from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="telemal",
    version="1.2.22",
    description="Get intelligence on malicious Telegram channels using bot Token",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicolasmf/Telemal",
    author="TA1GA",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["telemal=telemal.telemal:main"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
