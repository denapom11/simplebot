"""This Webex teams bot does the following"""
from flask import Flask, jsonify,abort,request,redirect
import requests
from webexteamssdk import WebexTeamsAPI
import sys, getopt
import json
from pprint import pprint
import csv
import random


# Configuration and parametes for WEBEX TEAMS
access_token=""
teamsapi = WebexTeamsAPI(access_token=access_token)
botid = ""

bot_functions = Flask(__name__)

@bot_functions.route('/handler', methods=['POST'])
def message_handler():
    '''Receives message, parses room_id and person_id.  Called on POST to /handler.'''
    message_data = json.loads(request.data)
    room_id = message_data["data"]["roomId"]
    person_id = message_data["data"]["personId"]
    room_type=message_data["data"]["roomType"]
    # Make sure bot doesn't respond to itself
    if person_id != botid:
        # Get the last x messages
        message_list = json.loads(get_messages(room_id,room_type))["items"]
        current_message = message_list[0]["text"]
        message_parser(room_id, current_message, person_id)
    
        
    return "message received"

def get_messages(room_id,room_type):
    headers = {"Authorization": f"Bearer {access_token}"}
    if room_type == "group":
        return requests.get(url=f"https://api.ciscospark.com/v1/messages?roomId={room_id}&max=10&mentionedPeople={botid}", \
        headers=headers).text 
    else:
        return requests.get(url=f"https://api.ciscospark.com/v1/messages?roomId={room_id}&max=10", \
        headers=headers).text
    


def message_parser(room_id, current_message, person_id):   
    teamsapi.messages.create(room_id, markdown=f"I just repeat what you say: echo {current_message}")

      
    
if __name__ == "__main__":
    # Start the web server
 
    # Code to get ngrok tunnel info so we don't have to set it manually
    # This will set our "url" value to be passed to the webhook setup
    tunnels = requests.request("GET", \
     "http://127.0.0.1:4040/api/tunnels", \
     verify=False)

    tunnels = json.loads(tunnels.text)
    tunnels = tunnels["tunnels"]

    url = ""
    for tunnel in tunnels:
        if tunnel['proto'] == 'https':
            url = tunnel['public_url']

    webhooks = teamsapi.webhooks.list()
    for webhook in webhooks:
        teamsapi.webhooks.delete(webhook.id)

    teamsapi.webhooks.create(name="simplebot",targetUrl=url+"/handler",resource="messages",event="created")

    bot_functions.run(host='0.0.0.0', port=5006, threaded=True, debug=False)