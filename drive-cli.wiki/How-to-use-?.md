The following commands are available at this point of time in drive-cli.

## help
 The help for any command in particular, or for the entire list of commands, can be displayed using the help 
 command.

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
    ls          list all the files present in this directory in the drive . 
                for tracked directories.  
    pull        get latest updates from online drive of the file.
    push        push modification from local files to the drive.
    rm          delete a particular file in drive.
    status      list changes committed since last sync.
    view-files  filter search files and file ID for files user has access to.
  ```

## login
It will open your browser and ask you to give permission to access  your google drive.
<p align="center">
    <img src="Demo.gif">
</p>

```sh

$ drive login #normal

$ drive --remote login #remote login

Usage: drive [remote or not] login [OPTIONS]

remote:
  --remote if you need to login to drive,on remote server without access to browser use this, it gives out a alter-link to login. 
Options:
  --help  Show this message and exit.
```
## view-files
 It displays all the files present in your drive recursively in the order of time stamp i.e. most recently used on top.
  ```sh
  $ drive view-files
  Usage: drive view-files [OPTIONS]

  view-files: Filter based list of the names and ids of the first 10 files
  the user has access to

Options:
  --name   provide username in whose repos are to be listed.
  --types  provide username in whose repos are to be listed.
  --pid    provide parent file ID or sharing link and list its child
           file/folders.
  --help   Show this message and exit.
  ```


## clone
 Downloads the file directory into the local machine
 ```sh
 $ drive clone fileID
 Usage: drive clone [OPTIONS] PAYLOAD

  clone: download a file/folder  using either the sharing link or using the
  file ID  for the file

Options:
  --help  Show this message and exit.
```

## add_remote
It will upload all files present in your current directory to your google drive.
```sh
$ drive add_remote 
Usage: drive add_remote [OPTIONS]

  add_remote: create remote equivalent for existing file/folder in local
  device

Options:
  --file TEXT  specify the partcular file to uploaded else entire directory is
               uploaded
  --pid TEXT   specify particular folder id/sharing_link of the folder under
               which remote must must be added
  --help       Show this message and exit.
```
## cat
Cat (concatenate) reads data from file and give their content as standard output without having to downloading the file itself.
```
$ drive cat 
Usage: drive cat [OPTIONS] LINK

  cat: reads data from file and give their content as output current
  file.

Options:
  --help  Show this message and exit.

Usage:
  $ drive cat 19lQAGxv21h55mrOziROImdltB_TS9dgQkboghQuk9qg

 Choose type to export to
 (ENTER to select, s to stop):

 => pdf
    txt
    doc
    zip
    html
    rtf
    odt
```
## rm
  This commands delete a particular file or folder
  
  ```sh
    Usage: drive rm [OPTIONS]

  rm: delete a particular file/folder from the directory in the remote drive

Options:
  --file TEXT  specify the partcular file to deleted else entire directory is
               deleted
  --id TEXT    delete untracked file directly using id or sharing link, can be
               used even for unlinked files
  --help       Show this message and exit.
  
  ```

## ls
List all the files present in the current directory only if the directory is set as remote to the directory in drive.

```sh
$ drive ls 
Usage: drive ls [OPTIONS]

  ls: Print files belonging to a folder in the drive folder of the current
  directory

Options:
  --help  Show this message and exit.
```
## status
It shows any changes done(creation,deletion,changes) to the directory after it was last uploaded.
The directory must be set as remote (add_remote).
```sh
$ drive status
Usage: drive status [OPTIONS]

  status: get a change log of files changed since you had the last
  sync(push/pull/clone)

Options:
  --help  Show this message and exit.
```
## pull
It is used to get the latest updates from an online drive of the file. It checks for the changes that is made in the drive for uploaded folder or file and downloads it locally.

```
$ drive pull
Usage: drive pull [OPTIONS]

drive pull: get latest updates from an online drive of the file.

Options:

--help: Show this message and exit
```
![drive_pull](https://user-images.githubusercontent.com/31641813/55322370-d3b38d80-5499-11e9-8a09-43cf515dda4e.PNG)

After pushing it to the drive it will be like this 

![Drive_pull](https://user-images.githubusercontent.com/31641813/55322879-188bf400-549b-11e9-8828-b6141befe726.PNG)


## push
It pushes any changes done to the directory to the drive.
```sh
$ drive push
Usage: drive push [OPTIONS]

  push the latest changes from your local folder that has been added/cloned
  to google drive.

Options:
  --help  Show this message and exit.
```
## History
Provides history of use of various functions in drive-cli for the current session

```sh
$ drive history
Usage: drive history [OPTIONS]

Options:
  --date TEXT  specify the date to filter out your history
  --clear      clear entire histroy
  --help       Show this message and exit.
```

 ## share
 ```sh
 Usage: drive share [OPTIONS] FID

  share file/folder using using either the sharing link or using the file ID

Options:
  --role TEXT     provide role to grant permission accordingly, following
                  roles are currently allowed :
                  * owner
                  * writer
                  * reader
                  [Default]:reader
  --type TEXT     type of grantee, following are currently available :
                  * user
                  * group
                  * anyone
                  [Default]:user
  --message TEXT  provide a short message you want to send
                  [Default]:'shared
                  via drive-cli'
  --help          Show this message and exit.
 ```
