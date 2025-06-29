"""
GOLEM - The Tesla/Apple of Discord Bots
Simple setup for transcendent bots
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="golem-discord",
    version="0.1.0",
    author="GOLEM Team",
    description="A revolutionary Discord bot framework where complexity dies and simplicity transcends",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/golem",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "discord.py>=2.3.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
        "psutil>=5.9.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "golem=golem:main",
        ],
    },
)