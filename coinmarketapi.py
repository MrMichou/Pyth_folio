import json
import pickle
import os.path
import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def google_data(value_crypto, sample_spreadsheet_id, sample_range_name):
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # The ID and range of a sample spreadsheet.

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Call the Sheets API
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    value_input_option = "RAW"
    # [START sheets_batch_update_values]
    crypto = []
    values = []
    values_crypto = []
    names_crypto = []
    #values.append(value_crypto[0])
    for i in value_crypto:
        values_crypto.append(float(value_crypto[i]))
        names_crypto.append(str(i))
    values.append(names_crypto)
    values.append(values_crypto)
    data = [
        {
            'range': sample_range_name,
            'values': values
        },
        # Additional ranges to update ...
    ]
    body = {
        'valueInputOption': value_input_option,
        'data': data
    }
    result = service.spreadsheets().values().batchUpdate(spreadsheetId=sample_spreadsheet_id, body=body).execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

def get_json(money, api_key):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
      'start':'1',
      'limit':'350',
      'convert': money
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    try:
      response = session.get(url, params=parameters)
      data = json.loads(response.text)
      with open('crypto.json', 'w') as f:
          json.dump(data, f)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e)

def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value

def process_data(symbol):
    symbol_crypto = []
    dict_crypto = {}
    for a in symbol.keys():
        symbol_crypto.append(a)
    with open('crypto.json') as file_data:
        data = json.load(file_data)
        print(data["status"]["timestamp"])
    for i in data["data"]:
        if i["symbol"] in symbol:
            append_value(dict_crypto, str(i["symbol"]), float(i["quote"]["CAD"]["price"]))
    return dict_crypto

def calc_total(dict_crypto, portefolio): 
    #print(portefolio.keys().items())
    total_win = 0
    total_portefolio = 0
    print("Cur \tPortefolio\t\tProfit \t\t\tMarket Value")
    for i in dict_crypto:
        for y in portefolio:
            if i == y:
                portefolio_value = portefolio[i][0] * dict_crypto[i]
                portefolio_win = portefolio_value - portefolio[i][1]
                total_win = total_win + portefolio_win
                total_portefolio = total_portefolio + portefolio_value 
                print(i + "\t" + str(portefolio_value) + "\t" + str(portefolio_win)  + "\t" + str(dict_crypto[i]))
    print("Profit : "+ str(total_win))
    print("Total protefolio : "+ str(total_portefolio))
    # return 


def main():
    spreadsheet_id = ""
    range_name = ""
    money = ''
    api_key = ''
    portfolio = {
            # Example
            # "The sign crypto : [Amount_crypto, how_much_you_put_in]]"
            "BTC"  : [1, 150000],
            "ETH"  : [1, 17000]
            }
    get_json(money, api_key)
    value_crypto = process_data(portfolio)
    calc_total(value_crypto, portfolio)
    # The google spreadsheet is a fucking nightmare to config
    google_data(value_crypto, spreadsheet_id, range_name)

main()
