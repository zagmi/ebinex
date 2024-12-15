import importlib
from setuptools import setup, find_packages

module = importlib.import_module('ebinexpy.version')
version = module.__version__

def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()


setup(
    name="ebinexpy",
    version=version,
    author="Santiago Ramirez",
    author_email="santiirepair@gmail.com",
    description="📈 The only and most reliable bridge between the broker and you.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zagmi/ebinex",
    packages=find_packages(),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements("requirements.txt"),
)
