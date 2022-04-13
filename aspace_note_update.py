"""aspace_note_update.py"""
#This script modifies or deletes a specific note type in ArchivesSpace based on information supplied by the user.
#The user can select whether their input must simply be contained in the original note text, or if it must exactly match the original note content.
#String matches to user input are case sensitive.
#This script is adapted from the advancedNoteEdit.py script created by the Rockefeller Archives Center. We borrow their original code with much gratitude.

#!/usr/bin/env python

import os, requests, json, sys, logging, configparser, urllib
from datetime import datetime

starttime = datetime.now()

config = configparser.ConfigParser()
config.read('local_settings.cfg')

#Logging setup
logging.basicConfig(filename='script_note_edits.txt', format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Starting script")

dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
repositoryBaseURL = '{baseURL}/repositories/{repository}'.format(**dictionary)
resourceURL = '{baseURL}'.format(**dictionary)

resource_containers = []

#Session authentication
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

def promptForIdentifier():
	#identifier is the numerical value at the end of the URI
	identifier = input("Please enter a resource identifier (must be integer): ")
	if identifier:
		return identifier
	else:
		print('You did not enter anything!')
		promptForIdentifier()

def getResourceObjects(identifier, headers, resource_containers):
	tree = requests.get(repositoryBaseURL + "/resources/" + identifier + "/tree", headers=headers).json()
	refList = getRefs(tree["children"], resource_containers)
	return refList

def getRefs(data, resource_containers):
	for component in data:
		resource_containers.append(component["record_uri"])
		if component["has_children"]:
			getRefs(component["children"], resource_containers)
	return resource_containers

def deleteNotesPartial(headers):
# Deletes notes that include input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["jsonmodel_type"] == "note_singlepart":
                if n["type"] == notetype:
                    for content in n["content"]:
                        del notes[index]
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logger.info(f'Deleted note with "{notecontent}" content in "{object_uri}" in resource number "{identifier}". The original note content was "{n["content"]}".')
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent in subnote["content"]:
                        del notes[index]
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logger.info(f'Deleted note with "{notecontent}" content in "{object_uri}" in resource number "{identifier}". The original note content was "{subnote["content"]}".')

        except:
            pass

def deleteNotesExact(headers):
# Deletes notes that match input notecontent exactly
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["jsonmodel_type"] == "note_singlepart":
                if n["type"] == notetype:
                    for content == n["content"]:
                        del notes[index]
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logger.info(f'Deleted note with "{notecontent}" content in "{object_uri}" in resource number "{identifier}". The original note content was "{n["content"]}".')
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"]:
                        del notes[index]
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logger.info(f'Deleted note with "{notecontent}" content in "{object_uri}" in resource number "{identifier}". The original note content was "{subnote["content"]}".')

        except:
            pass

def replaceNotesPartial(headers):
# Replaces notes that include input notecontent
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent in subnote["content"]:
                        subnote["content"] = replacecontent
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logger.info(f'Replaced previous note "{notecontent}" with "{replacecontent}" in "{object_uri}" in resource number "{identifier}". The original note content was "{subnote["content"]}".')
        except:
            pass

def replaceNotesExact(headers):
# Replaces notes that match input notecontent exactly
    notes = ao["notes"]
    for index, n in enumerate(notes):
        try:
            if n["type"] == notetype:
                for subnote in n["subnotes"]:
                    if notecontent == subnote["content"]:
                        subnote["content"] = replacecontent
                        post = requests.post('{baseURL}'.format(**dictionary) + str(aoId), headers=headers, data=json.dumps(ao))
                        logger.info(f'Replaced previous note "{notecontent}" with "{replacecontent}" in "{object_uri}" in resource number "{identifier}". The original note content was "{subnote["content"]}".')
        except:
            pass

#User input
identifier = promptForIdentifier()
objectlevel = input('Enter archival object level (e.g., series, file, otherlevel): ')
notetype = input('Enter the type of note (use EAD note types, e.g. accessrestrict, odd): ')
notecontent = input('Enter note content: ')
matchtype = input('Exact or partial string match? (exact/partial) ')
modifydelete = input('Modify notes or delete notes? (modify/delete) ')
if modifydelete == 'modify':
    replacecontent = input('New note content: ')
print('Getting a list of archival objects')
aoIds = getResourceObjects(identifier, headers, resource_containers)
for aoId in aoIds:
    ao = (requests.get('{baseURL}'.format(**dictionary) + str(aoId), headers=headers)).json()
    boxfolder = []
    levels = ao["level"]
    object_uri = ao['uri']
    if  modifydelete == 'delete' and levels == objectlevel:
        if matchtype == 'exact':
            deleteNotesExact(headers)
        elif matchtype == 'partial':
            deleteNotesPartial(headers)
    elif modifydelete == 'modify' and levels == objectlevel:
        if matchtype == 'exact':
            replaceNotesExact(headers)
        elif matchtype == 'partial':
            replaceNotesPartial(headers)

#Logging
logger.info("Script finished")
job_time = (datetime.now() - starttime)
logger.info(f' Job time: {job_time}')

logline_count = len(open('script_note_edits.txt').readlines())
edits_count = logline_count - 3
logger.info(f' Number of changes made: {edits_count}')
