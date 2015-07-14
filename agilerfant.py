#! /usr/bin/env nix-shell 
#! nix-shell -i python3 -p python3 python34Packages.requests2

import argparse
import requests
import time
import sys
import os

class Backlog(object):
    '''Handles requests to Agilefant'''

    AGILEFANT_SITE = "http://agilefant.cosc.canterbury.ac.nz:8080/agilefant302"

    def __init__(self, backlog_id):
        self.session = requests.Session() 
        self.backlog_id = backlog_id

    def post(self, path, payload):
        '''Makes a POST request. Returns said request'''
        return self.session.post(self.AGILEFANT_SITE + path, params = payload)

    def get_project_id(self):
        payload = {'backlogId': self.backlog_id}    
        r = self.post("/ajax/retrieveSubBacklogs.action", payload)
        return r.json()[0]['id']

    def get_iteration_ids(self):
        iteration_ids = []
        payload = {'projectId': self.get_project_id()}
        r = self.post("/ajax/projectData.action", payload) 
        for iteration in r.json()['children']:
            iteration_ids.append(iteration['id'])
        return iteration_ids

    def get_task_id(self, story_name, task_name):
        for iteration_id in self.get_iteration_ids():
            payload = {'iterationId': iteration_id}
            r = self.post("/ajax/iterationData.action", payload)
            for story in r.json()['rankedStories']:
                if story['name'] == story_name:
                    for task in story['tasks']:
                        if task['name'] == task_name:
                            return task['id']

    def log_task_effort(self, task_id, description, minutes_spent, user_ids):
        payload = {'parentObjectId': task_id,
                   'hourEntry.date': time.strftime("%s000"),
                   'hourEntry.minutesSpent': minutes_spent,
                   'hourEntry.description': description,
                   'userIds': user_ids}
        self.post("/ajax/logTaskEffort.action", payload)

    def login(self, username=None, password=None):
        '''Log in to Agilefant. This will create a session cookie which is used 
        to authorise other actions'''
        payload = {'j_username': username, 'j_password': password}
        r = self.post("/j_spring_security_check", payload)
        if r.text == "AGILEFANT_AUTHENTICATION_ERROR":
            print(r.text, file=sys.stderr)
            exit(1)

class Agilerfant(object):
    '''Command line interface to Agilefant'''

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="A command line interface for Agilefant",
            usage="""agilerfant <command> [<args>]
Possible agilerfant commands are:
    log      Log effort for a task
    rmlog    Delete logged effort
""")
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print("Unrecognised command")
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def log(self):
        parser = argparse.ArgumentParser(
            description="Log effort for a task") 
        parser.add_argument("-u", "--username", help="Agilefant username",
                type=str)
        parser.add_argument("-p", "--password", help="Agilefant password",
                type=str)
        parser.add_argument("-b", "--backlog", help="Backlog ID",
                type=int)
        args = parser.parse_args(sys.argv[2:])
        if args.username == None:
            args.username = os.environ['AGILEFANT_USER']
        if args.password == None:
            args.password = os.environ['AGILEFANT_PASSWORD']
        if args.backlog == None:
            args.backlog = os.environ['AGILEFANT_BACKLOG']
        backlog = Backlog(args.backlog)
        backlog.login(args.username, args.password)

    def rmlog(self):
        parser = argparse.ArgumentParser(
            description="Delete logged effort")
        parser.add_argument("repository")

if __name__ == "__main__":
    Agilerfant()
