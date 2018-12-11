"""
Backs up the database file to Dropbox.
Code is basically stolen from Dropbox example
This is an example app for API v2.
"""

import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

import pirata_codex as pc
from pirata_codex.config import *
# Add OAuth2 access token here.
# You can generate one for yourself in the App Console.
# See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>

# Uploads contents of LOCALFILE to Dropbox
def backup(local_name, backup_name):
    with open(local_name, 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading " + local_name + " to Dropbox as " + backup_name + "...")
        try:
            dbx.files_upload(f.read(), backup_name, mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                err.error.get_path().reason.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()


# Restore the local and Dropbox files to a certain revision
def restore(rev=None):
    # Restore the file on Dropbox to a certain revision
    print("Restoring " + BACKUPPATH + " to revision " + rev + " on Dropbox...")
    dbx.files_restore(BACKUPPATH, rev)
    # Download the specific revision of the file at BACKUPPATH to LOCALFILE
    print("Downloading current " + BACKUPPATH + " from Dropbox, overwriting " + LOCALFILE + "...")
    dbx.files_download_to_file(LOCALFILE, BACKUPPATH, rev)

# Look at all of the available revisions on Dropbox, and return the oldest one
def select_revision():
    # Get the revisions for a file (and sort by the datetime object, "server_modified")
    print("Finding available revisions on Dropbox...")
    entries = dbx.files_list_revisions(BACKUPPATH, limit=30).entries
    revisions = sorted(entries, key=lambda entry: entry.server_modified)
    for revision in revisions:
        print(revision.rev, revision.server_modified)
    #return the oldest revision (first entry, because revisions was sorted oldest:newest)
    return revisions[0].rev

if __name__ == '__main__':
    discord = pc.Discord()
    try:
        # Check for an access token
        if 'dropbox' not in configs.keys() and 'token' not in configs['dropbox'].keys():
            sys.exit("ERROR: Looks like you didn't add your access token. "
                     "Open up backup-and-restore-example.py in a text editor and "
                     "paste in your token in line 14.")
    
        # Create an instance of a Dropbox class, which can make requests to the API.
        print("Creating a Dropbox object...")
        dbx = dropbox.Dropbox(configs['dropbox']['token'])
    
        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
        except AuthError as err:
            sys.exit("ERROR: Invalid access token; try re-generating an "
                     "access token from the app console on the web.")

        # Create a backup of the current settings file
        backup( BASEDIR + configs['database']['db_name'],
                configs['dropbox']['backup_path'])
    except:
        discord.send('Database Backup Failed')
    else:
        discord.send('Database Backup was Successful')
    
