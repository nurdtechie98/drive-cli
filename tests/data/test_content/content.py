help_text = '''
Usage: drive [OPTIONS] COMMAND [ARGS]...
Options:
  --remote  remote login in case browser is on a different machine
  --help    Show this message and exit.
Commands:
  add-remote  upload any existing file to drive
  cat         view contents of the file using its file id or sharing link
  clone       download any file using sharing link or file ID it will be
              automatically tracked henceforth
  login       login to your google account and authenticate the service
  logout      logout from the account logged in with
  ls          list out all the files present in this directory in the drive
              for tracked directories
  pull        get latest updates from online drive of the file
  push        push modification from local files to the drive
  rm          delete a particular file in drive
  status      list changes committed since last sync
  view-files  filter search files and file ID for files user has access to
  '''
