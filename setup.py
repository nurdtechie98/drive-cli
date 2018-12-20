from setuptools import setup, find_packages

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except:
        pass

setup(
    name ='Drive-CLI',
    version ='1.0',
    description = 'Upload your files to Google Drive without leaving the terminal',
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
        'httplib2'
    ],
    entry_points='''
        [console_scripts]
        drive=main:cli
        
    ''',
)