Pirata - Codex
--------------

This will be a lightweight piece of code for tracking player activity 
levels in Clash of Clans, will include an sqlite3 database structure and 
mechanisms for running web requests to the Clash API and Discord.

Lots of things are linked to jsons in a `data/` folder, which includes 
private information. Maybe one day I'll upload examples but for now the folder
won't be added here.

`config.py`
===========
Includes constants used in code, would need to be updated if installed elsewhere. 
Should reconcile these with the `data/` json's but not a priority at the moment

`clash.py`
=========
The class for communicating with the Supercell API and getting back jsons

`database.py`
=========
Contains the definitions of the sqlite database for use with SQL Alchemy

`database_utils.py`
=========
Helper functions for populating and maintaining the databases

`activity.py`
=========
Functions for querying the database to get player activity


`bin/scripts.py`
=========
The actual scripts I have running daily on cronjobs
