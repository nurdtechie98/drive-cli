<p align="center">
  <a href="" rel="noopener">
 <img height=200px src="./logo.svg" alt="Briefly-logo"></a>
</p>

<h1 align="center">Drive Cli</h1>

<div align="center">

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org/download/releases/3.4.0/)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/nurdtechie98/drive-cli/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HitCount](http://hits.dwyl.io/nurdtechie98/drive-cli.svg)](http://hits.dwyl.io/nurdtechie98/drive-cli)

<h4>Get the ability to access <strong>Google Drive</strong> without leaving your terminal.</h4>

</div>
-----------------------------------------
### Inspiration

* Google Drive has become a vital part of our day to day life. As much as non-programmer use it, so do programmers in several situations,where we need not use git/github. 

* Drive-CLI is a command line utility tool for google drive which helps you access,sync, download,upload.. directly to your drive without leaving the command line. The best part being the commands are similar to git cli so that you can easily remember them :massage:  

------------------------------------------
### Features

- `view-file` :list your files, filter them by name,type.
- `clone` :download file/folder from drive using sharing link or file ID and get it linked 
- `add_remote` :upload existing local file to drive and get it linked
- `rm` :remove particular file or folder
- `ls` :list put all the files present in the drive of equivalent current directory
- `status` :list changes made to local files since last pull or pull
- `pull` :get latest changes from drive to local files
- `push` :push the changes made in remote to drive

------------------------------------------
### Installation

* Clone the directory
```sh
        $ git clone https://github.com/nurdtechie98/drive-cli.git
```
* Install the requirements
```sh
    $ cd drive-cli
    $ pip install -e . #note the dot
```
* Login to Your Account
```sh
    $ python main.py
```
> select the account to login with and you are good to go :dancers:
------------------------------------------
### Usage
* Once installation and login is done, just use `drive` and the required command.
* Use `drive --help` for listing all the commands
* Use  `drive [command] --help` to list all the options available for each command
------------------------------------------
### Uninstalling

```sh
    $ pip uninstall Drive_CLI
```
------------------------------------------
### Contributing

 * We're are open to `enhancements` & `bug-fixes` :smile:.
 * Feel free to add issues and submit patches

------------------------------------------
### Author
Chirag Shetty - [nurdtechie98](https://github.com/nurdtechie98)

See also the list of [contributors](https://github.com/nurdtechie98/drive-cli/graphs/contributors) who participated in this project.

------------------------------------------
### License
This project is licensed under the MIT - see the [LICENSE](./LICENSE) file for details

