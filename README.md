# Gmail Cleanup

## Overview

Let's say you don't want to pay for an email marketing platform. Instead, you write a Python script to send emails to your distribution lists.

How do you process unsubscribe requests and failed deliveries? With <b>gmail_cleanup</b>!

## Installing / Getting Started

```shell
conda create --name <env> --file requirement requirements.txt
conda activate <env>
python process_inbox.py
```

`process_inbox.py` will scrub your inbox for the messages identified as unsubscribe requests and failed deliveries.

### Initial Configuration

### Google API Credentials
You'll need to set up API credentials to:
1. Gmail
2. Google Sheets

I saved them in `/config/gmail/` and `/config/sheets/` respectively. Specify these paths in `secrets.py` (obviously not shown here).

### Gmail
1. In Gmail, set up filters to label and archive messages matching certain criteria.
2. We need the label IDs (e.g., Label_1234567890123456789) for each label you want to scrub. To get them, I used the following code:
```
results = service.users().messages()
messages_list = results.list(userId = str_id_email, maxResults = None).execute() # need to execute
for dict_msg in messages_list['messages']: # list of dicts {'id': id}
    message_id = dict_msg['id']
    dict_results = results.get(userId = str_id_email, id = message_id, format = 'metadata').execute()
    print(dict_results.keys())
    if {'name': 'Subject', 'value': 'Delivery Status Notification (Failure)'} in dict_results['payload']['headers']: 
        print(dict_msg['id'])
        break
```

### Google Sheets
1. Set up a Google Sheet and share it with the Python script via the email in the credentials JSON (see links below).

## Features

* scrub Gmail inbox for specific labels and log the relevant emails in a Google sheet

## Helpful Links

- Gmail API Quickstart<br>
https://developers.google.com/gmail/api/quickstart/python
- README.md<br>
https://github.com/jehna/readme-best-practices
- Troubleshooting Label ID Usage<br>
https://stackoverflow.com/questions/26963868/gmail-api-invalid-label-when-trying-to-set-message-label-to-one-that-i-create
- Read and Update Google Spreadsheets with Python!<br>
https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/