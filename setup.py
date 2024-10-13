from setuptools import setup

setup(
    name="telemal",
    version="1.2",
    description="Get intelligence on malicious Telegram channels using bot Token",
    url="https://github.com/nicolasmf/Telemal",
    author="TA1GA",
    license="MIT",
    packages=["telemal"],
    entry_points={
        "console_scripts": ["telemal=telemal.telemal:main"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
