from typing import Optional
import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

ascii_art = '''
                                                                      
                 █▄█ █▀█ ▀█▀ █   █ █ █ █ █▀█ ▀█▀ █▀▀ █▀▄              
                 █ █ █▀█  █  █   █▀█ █ █ █ █  █  █▀▀ █▀▄              
                 ▀ ▀ ▀ ▀ ▀▀▀ ▀▀▀ ▀ ▀ ▀▀▀ ▀ ▀  ▀  ▀▀▀ ▀ ▀                                                                        
'''
load_dotenv()
intelx_token = os.getenv('INTELX_TOKEN')

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 11.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5520.225 Safari/537.36",
           "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate",
           "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://phonebook.cz",
           "Dnt": "1", "Referer": "https://phonebook.cz/", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors",
           "Sec-Fetch-Site": "cross-site", "Te": "trailers"}

def fetch_token(domain:str)->dict:
    """
    Retrieves a token from the Intelx API for a given domain.
    Args:
        domain (str): The domain for which the token is requested.
        token (str): The token to use for authentication.
    Returns:
        dict: The token retrieved from the Intelx API as a Python object.
    Raises:
        SystemExit: If the status code is 401(unauthorized) 402 (daily limit) or 403 (blacklisted IP),
                    or if there's an error parsing the response content.
    """
    try:
        url = f"https://2.intelx.io:443/phonebook/search?k={intelx_token}"
        payload = {
        "maxresults": 10000,
        "media": 0,
        "target": 2,
        "term": domain,
        "terminate": [None],
        "timeout": 20
        }

        response = requests.post(url, headers=headers, json=payload, timeout=5)
        status = response.status_code
        if status == 401:
            sys.exit('❗ Request Failed. Invalid credentials.')
        elif status == 402:
            sys.exit('❗ Your IP is rate limited or you have reached your daily limit.')
        elif status == 403:
            sys.exit('❗ Request Failed! Your IP address might have been blacklisted.')
        else:
            return response.text
    except requests.exceptions.RequestException as e:
        sys.exit(f'❗ Request Failed! {e}')


def get_query_results(token:str)->str:
    """
    Sends a GET request to the Intelx API to retrieve the search results for a given API key.
    Args:
        api_key (str): The API key retrieved from the Intelx API.
    Returns:
        str: The items found in the search results.
    Raises:
        SystemExit: If the status code is 402 (rate limit error) or 403 (blacklisted IP error).
    """
    if not token:
        sys.exit('❗ Empty API key provided.')
    try:
        key_id = json.loads(token)["id"]
    except json.JSONDecodeError:
        sys.exit('❗ Invalid JSON format for the intelx token.')

    url = f"https://2.intelx.io:443/phonebook/search/result?k={intelx_token}&id={key_id}&limit=1000000"
    response = requests.get(url, headers=headers, timeout=5)
    items = response.text
    status = response.status_code
    if status == 401:
        sys.exit('❗ Request Failed. Invalid credentials.')
    elif status == 402:
        sys.exit('❗ Your IP is rate limited. Try switching your IP address then re-run.')
    elif status == 403:
        sys.exit('❗ Request Failed! Your IP address might have been blacklisted.')
    else:
        return items


def parse_results(data: str, args: Optional[str] = None) -> None:
    """
    Parses a JSON string to extract a list of results and 
    performs different actions based on the provided arguments.

    Args:
        data (str): A JSON string containing a list of results with the 'selectorvalue' key.
        args (str, optional): The output file name. If provided, 
        the results will be saved to a file. Defaults to None.

    Returns:
        None
    """
    try:
        data = json.loads(data)['selectors']
        results = [item['selectorvalue'] for item in data]
        num_results = len(results)
        if args.output:
            try:
                print(f"\n🔍 {num_results} result(s) found.")
                with open(args.output + '.txt', 'a',encoding="UTF-8") as file:
                    file.write('\n'.join(results))
                print(f'\n✅ Done! Saved to {args.output}.txt')
            except IOError as e:
                print(f'❌ Error saving to file: {e}')
        else:
            if num_results <= 30:
                print(f"🔍 {num_results} result(s) found:")
                for result in results:
                    print(result)
            else:
                print(f"\n🔍 {num_results} result(s) found.")
                choice = input("Do you want to save results to a file? (yes/no): ")
                if choice.lower() in ['yes', 'y']:
                    try:
                        filename = input("Enter filename: ")
                        with open(filename + '.txt', 'a',encoding="UTF-8") as file:
                            file.write('\n'.join(results))
                        print(f'\n✅ Done! Saved to {filename}.txt')
                    except IOError as e:
                        print(f'❌ Error saving to file: {e}')
                else:
                    print('\n❗ Results not saved.')
                    choice = input("Do you want to print all results to terminal? (yes/no): ")
                    if choice.lower() == 'yes':
                        for result in results:
                            print(result)
                    else:
                        print('stopping...')
    except json.JSONDecodeError as e:
        print(f'❌ Error decoding JSON: {e}')

def argparser():
    """
Parses a JSON string to extract a list of items and 
performs different actions based on the provided arguments.

Args:
    items (str): A JSON string containing a list of items with the 'selectorvalue' key.
    args (str, optional): The output file name. If provided, 
    the items will be saved to a file. Defaults to None.

Returns:
    None
"""
        
    parser = argparse.ArgumentParser(description="MailHunter")
    parser.add_argument("-d", "--domain", help="Searches all emails for provided domain.")
    parser.add_argument('-o', '--output', help='Output file name')
    return parser.parse_args()

if __name__ == '__main__':
    print(ascii_art)
    print('🚀 Running MailHunter!')
    args = argparser()
    if args.domain:
        token = fetch_token(args.domain)
        emails = get_query_results(token)
        parse_results(emails,args)

#TODO api check credential leaks