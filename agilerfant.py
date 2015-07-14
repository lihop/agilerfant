#! /usr/bin/env nix-shell 
#! nix-shell -i python3 -p python3 python34Packages.requests2

import argparse
import requests
import getpass
import time
import sys
import os

class Backlog(object):
    '''Handles requests to Agilefant'''

    AGILEFANT_SITE = "http://agilefant.cosc.canterbury.ac.nz:8080/agilefant302"

    def __init__(self, backlog_id=None):
        self.session = requests.Session() 
        self.backlog_id = backlog_id

    def post(self, path, payload=None):
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

    def get_user_id(self, name):
        '''Takes either the full name or username of a user and returns
        Agilefant's internal user id for that user'''
        r = self.post("/ajax/retrieveAllUsers.action")
        for user in r.json():
            if user['name'] == name or user['fullName'] == name:
                return user['id']

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
        self.backlog = Backlog()

    def log(self, args):
        task_id = self.backlog.get_task_id(args.story_name, args.task_name)
        user_id = [self.backlog.get_user_id(args.username)]
        self.backlog.log_task_effort(task_id, args.description, args.time_spent,
                user_id)

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", "--username", help="Agilefant username",
                type=str)
        parser.add_argument("-p", "--password", help="Agilefant password",
                type=str)
        parser.add_argument("-b", "--backlog", help="Backlog ID",
                type=int)
        subparsers = parser.add_subparsers()
        parser_log = subparsers.add_parser("log")
        parser_log.add_argument("story_name", type=str,
                help="Name of the story which task belongs to")
        parser_log.add_argument("task_name", type=str,
                help="Name of the task to log effort for")
        parser_log.add_argument("time_spent", type=str,
                help="Time spent on the task")
        parser_log.add_argument("-d", "--description", help="Description",
                type=str)
        parser_log.set_defaults(func=self.log)
        args = parser.parse_args()
        if args.username == None:
            try:
                args.username = os.environ['AGILEFANT_USER']
            except:
                args.username = input("Username: ")
        if args.password == None:
            try:
                args.password = os.environ['AGILEFANT_PASSWORD']
            except:
                args.password = getpass.getpass()
        if args.backlog == None:
            try:
                args.backlog = os.environ['AGILEFANT_BACKLOG']
            except:
                args.backlog = input("Backlog: ")
        self.backlog.backlog_id = args.backlog
        self.backlog.login(args.username, args.password)
        args.func(args)

if __name__ == "__main__":
    Agilerfant().main()
