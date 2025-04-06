from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="lego-mosaic-generator",
    version="0.1.0",
    author="Lego Mosaic Generator Contributors",
    author_email="your.email@example.com",
    description="A GUI application to convert images into Lego mosaic designs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/lego-mosaic-generator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "lego-mosaic=lego_mosaic_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["Lego Colors.xlsx"],
    },
) 