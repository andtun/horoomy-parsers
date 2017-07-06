# This Python file uses the following encoding: utf-8

import dropbox
from dropbox.files import WriteMode

REMOTE_ROOT = '/Приложения/hoROOMy/'
TOKEN = 'RooTI79s2tAAAAAAAAAAL-6ZAv5-hU0vsILShL8XRDbRiQXgXpReUYd9p09b6l33'
DBX = dropbox.Dropbox(TOKEN)


class BackuppedFile:
    filename = ''
    DBXfilename = ''
    fileBytes = None
    #dbx = None

    def __init__(self, filename):
        self.filename = filename
        fname = filename
        if '/' in fname:
            fname = fname[fname.rfind('/')+1:]
        self.DBXfilename = REMOTE_ROOT+fname
        self.fileBytes = open(filename, 'rb').read()
        #self.dbx = dropbox.Dropbox(TOKEN)

    def upload(self):
        DBX.files_upload(self.fileBytes, self.DBXfilename, mode=WriteMode('overwrite'))
        
    def sync(self):
        DBX.files_download_to_file(self.filename, self.DBXfilename, rev=None)

