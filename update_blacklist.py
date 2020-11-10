# general
import sys

# google
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# data
import pandas as pd

# secrets
import secrets

# consts
gbl_str_path_cred_json = secrets.gbl_str_path_cred_json
gbl_str_workbook_name = secrets.gbl_str_workbook_name

def get_creds(str_path_cred_json):

    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name(str_path_cred_json, scope)

    return creds

def get_client(creds):
    # authorize the clientsheet 
    client = gspread.authorize(creds)
    return client

def get_sheet(client, str_workbook_name, int_sheet = 0):
    sheet = client.open(str_workbook_name)
    sheet_instance = sheet.get_worksheet(int_sheet) # get the first sheet of the Spreadsheet
    return sheet_instance

def get_sheet_df(sheet_instance):
    records_data = sheet_instance.get_all_records()
    df_records = pd.DataFrame.from_dict(records_data)
    return df_records

def append_sheet(sheet_instance, df_append):
    df_records = get_sheet_df(sheet_instance)
    sheet_instance.insert_rows(df_append.values.tolist(), row = len(df_records.index)+2) # 2 = 1 for header + 1 for next row
    return

def update_blacklist(df_records):
    creds = get_creds(gbl_str_path_cred_json)
    client = get_client(creds)
    sheet_instance = get_sheet(client, gbl_str_workbook_name)
    append_sheet(sheet_instance, df_records)
    return

if __name__ == "__main__":

    if len(sys.argv) > 1:

        # for testing purposes only,
        # here's an example of how this
        # module works

        # create exmample df to append

        ls_emails_fail = ["fake" + str(i) + "@gmail.com" for i in range(0,3)]
        
        dict_append = {}
        int_key = 0
        for str_email_fail in ls_emails_fail:
            dict_append[int_key] = [str_email_fail, "DF"]
            int_key += 1
            
        df_append = pd.DataFrame.from_dict(
            dict_append,
            orient = 'index',
            columns = ['email_address', 'blacklist_code']
        )

        # update
        update_blacklist(df_append)