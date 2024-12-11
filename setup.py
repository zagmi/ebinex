from setuptools import setup, find_packages

def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()

setup(
    name='ebinexpy',
    version='0.1.0',
    author='Santiago Ramirez',
    author_email='santiirepair@gmail.com',
    description='📈 EbinexPy is a library to easily interact with ebinex.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SantiiRepair/ebinexpy',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=read_requirements('requirements.txt'),
)
