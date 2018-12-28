from drive_cli import __version__
from setuptools import setup, find_packages
from setuptools.command.install import install

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except:
        pass

setup(
    name ='drive_cli',
    version='.'.join(str(i) for i in __version__),
    description = 'CLI client for Google Drive',
    url='https://github.com/nurdtechie98/drive-cli',
    author = 'Chirag Shetty',
    author_email = 'nurdtechie98@gmail.com',

    long_description=readme(),  
    long_description_content_type='text/markdown',
    
    packages = find_packages(),
    include_package_data = True,
    install_requires=[
        'requests',
        'click',
        'colorama',
        'windows-curses;platform_system=="Windows"',
        'pick',
        'google-api-python-client',
        'oauth2client',
        'prettytable',
        'httplib2',
        'pyfiglet'
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