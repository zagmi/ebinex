from setuptools import setup, find_packages

def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()


setup(
    name="ebinexpy",
    version="0.1.0",
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
