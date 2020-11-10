# google
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# general
import time
import csv
from datetime import datetime

# data
import pandas as pd

# blacklist
import update_blacklist as ub

# import secrets
import secrets

# constants

# specify old/new labels for unsubscribe and DSNF
dict_labels = {
    'unsubscribe': {
        'filter': "Label_3254612353444124080",
        'python': "Label_1657932202594091565"
    },
    'DSNF': {
        'filter': "Label_8167218948811887935",
        'python': "Label_6150393955522464486"
    }
}

# https://developers.google.com/gmail/api/auth/scopes
# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

str_path_pickle = secrets.str_path_pickle
str_path_cred = secrets.str_path_cred
str_id_email = secrets.str_id_email
ls_target_labels = secrets.ls_target_labels

def get_creds(str_path_cred, str_path_pickle):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(str_path_pickle):
        with open(str_path_pickle, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str_path_cred, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(str_path_pickle, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_service(creds):
    service = build('gmail', 'v1', credentials=creds)
    return service

if __name__ == "__main__":

    # get messages
    creds = get_creds(str_path_cred, str_path_pickle)
    service = get_service(creds)
    messages = service.users().messages()

    # get data
    dict_append = {}
    int_key = 0 # index for df from dict_append
    for str_key in dict_labels.keys():

        request = None
        while True:

            # Get (next) block of message Ids
            if not request:
                request = messages.list(userId=str_id_email,
                                            maxResults=None,
                                            includeSpamTrash=False,
                                            labelIds=str_target_label)
            else:
                request = messages.list_next(previous_request=request,
                                                previous_response=response)
            
            # exit if nothing
            if not request:
                break
            response = request.execute()
            
            # Get headers for messages in the message block
            if not response['messages']:
                break
            
            # get data
            for message in response['messages']:
                message_id = message['id']
                message_request = messages.get(userId=str_id_email,
                                                    id=message_id,
                                                    format='metadata',
                                                    metadataHeaders = ['From', 'To', 'Subject', 'Date', 'X-Failed-Recipients']).execute()
            
                # get values
                dict_values = {}
                dict_values['id'] = message_request['id']
                dict_values['snippet'] = message_request['snippet']
                dict_values['labelIds'] = message_request['labelIds']
                for dict_header in message_request['payload']['headers']:
                    dict_values[dict_header['name']] = dict_header['value']
                
                # log
                print(", ".join(["processing", dict_values['id'], dict_values['From'], dict_values['To']]))

                # filter

                # DSNF ie Subject = Delivery Status Notification (Failure)
                # automatically filtered by gmail so I don't have to see it in my inbox
                if dict_labels['DSNF']['filter'] in dict_values['labelIds']: 
                
                    # writing the fields
                    dict_append[int_key] = [dict_values['X-Failed-Recipients'].strip().lower(), "DF"]
                    int_key += 1
                    
                    # update labels
                    # add DSNF_python
                    # remove DSNF_gmail (doesn't matter if not applied)
                    # https://developers.google.com/gmail/api/reference/rest/v1/users.messages/modify
                    # https://stackoverflow.com/questions/26963868/gmail-api-invalid-label-when-trying-to-set-message-label-to-one-that-i-create
                    messages.modify(userId=str_id_email, id=dict_values['id'], body={"addLabelIds":[dict_labels['DSNF']['python']], "removeLabelIds":[dict_labels['DSNF']['filter']]}).execute()

                    # log
                    print("DSNF, " + dict_values['X-Failed-Recipients'].strip().lower())

                # unsubscribe
                # either subject is "unsubscribe"
                # or "unsubscribe" is the first word in the snippet
                elif dict_labels['unsubscribe']['filter'] in  dict_values['labelIds']:

                    dict_append[int_key] = [dict_values['From'].strip().lower(), "U"]
                    int_key += 1

                    # update labels
                    # add unsubscribe_python
                    # remove unsubscribe_gmail (doesn't matter if not applied)
                    messages.modify(userId=str_id_email, id=dict_values['id'], body={"addLabelIds":[dict_labels['unsubscribe']['python']], "removeLabelIds":[dict_labels['unsubscribe']['filter']]}).execute()

                    # log
                    print("Unsubscribe, " + dict_values['From'].strip().lower())

                else:
                    pass
                    
                # wrap up
                time.sleep(1)

    # create append df
    df_append = pd.DataFrame.from_dict(
        dict_append,
        orient = 'index',
        columns = ['email_address', 'blacklist_code']
    )

    # update sheet
    ub.update_blacklist(df_append)

# roadmap
# TODO: make sure blacklist is just uniques / no dupes, make them all lower just in case
# TODO: backup?
# TODO: email me a summary of unsubs? DSNF?