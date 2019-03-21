<p align="center">
  <a href="" rel="noopener">
 <img height=200px src="https://i.imgur.com/QEcBZSh.png" alt="Briefly-logo"></a>
</p>

<h1 align="center">Drive Cli</h1>

<div align="center">

[![PyPI version](https://badge.fury.io/py/drive-cli.svg)](https://badge.fury.io/py/drive-cli)
[![Python version](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org/download/releases/3.4.0/)

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/nurdtechie98/drive-cli/issues)

[![Build Status](https://travis-ci.org/nurdtechie98/drive-cli.svg?branch=dev)](https://travis-ci.org/nurdtechie98/drive-cli)


[![Build Status](https://travis-ci.org/nurdtechie98/drive-cli.svg?branch=dev)](https://travis-ci.org/nurdtechie98/drive-cli)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HitCount](http://hits.dwyl.io/nurdtechie98/drive-cli.svg)](http://hits.dwyl.io/nurdtechie98/drive-cli)

<h4>Get the ability to access <strong>Google Drive</strong> without leaving your terminal.</h4>

</div>

-----------------------------------------
### Inspiration

* Google Drive has become a vital part of our day to day life. As much as non-programmers use it, so do programmers in several situations, where we need not use git/github. 

* Drive-CLI is a command-line utility for google drive which helps you access, sync, download, upload, etc. directly to your drive without leaving the command-line. The best part being the commands are similar to git CLI so that you can easily remember them :massage:  

------------------------------------------
### Features

- `view-files`: list your files; filter them by name, type.
- `clone`: download file/folder from drive using sharing link or file ID and get it linked.

- `add_remote`: upload existing local file to drive and get it linked.

- `add-remote`: upload existing local file to drive and get it linked.

- `add-remote`: upload existing local file to drive and get it linked.

- `cat`: view files contents of text format without actually downloading them.
- `rm`: remove particular file or folder.
- `ls`: list all the files present in the drive of equivalent current directory.
- `status`: list changes made to local files since last pull or pull.
- `pull`: get latest changes from drive to local files.
- `push`: push the local changes to drive.

------------------------------------------
### Demo
<p align="center">
    <img src="./Demo.gif">
</p>


------------------------------------------
### Installation
* For Usage
```sh
    #install using pip 
    $ pip install drive-cli
```
* For Development
    * clone the repo
    ```sh
        $ git clone https://github.com/nurdtechie98/drive-cli.git
    ```
    * get your `client_secret.json` from [Oauth](https://console.cloud.google.com/apis/credentials/oauthclient). Make sure to enable [Drive Api](https://console.cloud.google.com/apis/library/drive.googleapis.com?q=Drive) for the project.
    * rename the client secret to `oauth.json` and place it in the [drive_cli](./drive_cli) directory.
    * install the package:
    ```sh
        # move into package directory
        $ cd drive-cli
        # install package in edit mode
        $ pip install -e . #note the dot
    ```

------------------------------------------
### Usage


#### Help 
The help for any command in particular, or for the entire list of commands, can be displayed using the **help** command.
```sh
$ drive --help

Usage: drive [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add_remote  upload any existing file or folder to drive.
  clone       download any file using a sharing link or file ID. It will be
              automatically tracked henceforth.
  login       login to your google account and authenticate the service.
  logout      logout from the account logged in with.
  ls          list all the files present in this directory in the drive
              for tracked directories.
  pull        get latest updates from online drive of the file.
  push        push modification from local files to the drive.
  rm          delete a particular file in drive.
  status      list changes committed since last sync.
  view-files  filter search files and file ID for files user has access to.

```
#### Add Remote
Existing files or folders that have not been added to drive can be added and get tracked. 
In case you need to add a particular file, use the `file` parameter.
The file folder can also be added inside particular parent folder in the drive using the file id of the folder.

```sh
# adding entire folder named test to drive
$ cd test
$ drive add_remote
Created a tracked directory
uploading .DS_Store
uploading main.js
uploading test.html
uploading style.css

# adding a particular file (mailer.py) in current directory
$ drive add_remote --file mailer.py
uploaded mailer.py

#adding the file or folder inside particular parent file(test) using its file id
$ drive add_remote --file mailer.py --pid 1RJOWpW5MuP9RXpgZbp9OdauhaBtJd49g
uploaded mailer.py
content added under directory test

```


#### Clone
Download a file or folder present in drive using its file id or its sharing link. In case it is a folder it gets tracked.

```sh
# using file id note: since it is google doc it will be asked for a choice to select from
$ drive clone 1syTNkfXoc3pzpJSL0Z5LDioTFc46_LjzHjDDUvk90ks
Choose type to export to
 (ENTER to select, s to stop):

 => pdf
    txt
    doc
    zip
    html
    rtf
    odt
Preparing: watson script for download
downloading file  [####################################]  100%
completed download of watson script

# using file sharing link
$ drive clone https://docs.google.com/document/d/1syTNkfXoc3pzpJSL0Z5LDioTFc46_LjzHjDDUvk90ks
Choose type to export to
 (ENTER to select, s to stop):

 => pdf
    txt
    doc
    zip
    html
    rtf
    odt
Preparing: watson script for download
downloading file  [####################################]  100%
completed download of watson script

```

for further in depth documetation checkout our [wiki](https://github.com/nurdtechie98/drive-cli/wiki/How-to-use-%3F).


for further in depth documetation checkout our [wiki](https://github.com/nurdtechie98/drive-cli/wiki/How-to-use-%3F).


------------------------------------------
### Uninstalling

```sh
    $ pip uninstall drive-cli
```
------------------------------------------
### Contributing

 * We're are open to `enhancements` & `bug-fixes` :smile:. Take a look [here](./Contributing.md) to get started
 * Feel free to add issues and submit patches

------------------------------------------
### Author
Chirag Shetty - [nurdtechie98](https://github.com/nurdtechie98)

See also the list of [contributors](https://github.com/nurdtechie98/drive-cli/graphs/contributors) who participated in this project.

------------------------------------------
### License
This project is licensed under the MIT - see the [LICENSE](./LICENSE) file for details.

