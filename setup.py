from drive_cli import __version__
from setuptools import setup, find_packages


def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except:
        pass

setup(
    name='drive_cli',
    version='.'.join(str(i) for i in __version__),
    description='CLI client for Google Drive',
    url='https://github.com/nurdtechie98/drive-cli',
    author='Chirag Shetty',
    author_email='nurdtechie98@gmail.com',

    long_description=readme(),
    long_description_content_type='text/markdown',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests==2.21.0',
        'click==7.0',
        'colorama==0.4.1',
        'windows-curses;platform_system=="Windows"',
        'pick==0.6.4',
        'google-api-python-client==1.7.8',
        'oauth2client==4.1.3',
        'prettytable==0.7.2',
        'httplib2==0.12.1',
        'pyfiglet==0.8.post1'
    ],
    entry_points={
        'console_scripts': [
            'drive=drive_cli.dcli:cli'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
