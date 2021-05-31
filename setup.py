from setuptools import find_packages
from setuptools import setup

setup(
    name='gkeeptomd',
    version='0.0.0',
    description='Get notes from google keep and save them to a markdown file',
    author='twanh',
    author_email='huiskenstwan@gmail.com',
    packages=find_packages(),
    python_requires='>=3.9.0',
    install_requires=[
        'appdirs==1.4.4',
        'keyring==23.0.1',
        'gkeepapi==0.13.4',
    ],
    entry_points={
        'console_scripts': [
            'gkeeptomd=gkeeptomd.__main__:run',
        ],
    },
)
