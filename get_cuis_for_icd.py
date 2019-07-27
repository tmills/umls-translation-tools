#!/usr/bin/env python

from authenticate import Authentication
import argparse
import json
import requests
import sys
import time


# https://documentation.uts.nlm.nih.gov/terms-of-service.html
# NLM requires that users send no more than 20 requests per second per IP address

parser = argparse.ArgumentParser(description='Convert an input list of ICD9/10 codes into UMLS CUIs')
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "API key from your UTS Profile (https://uts.nlm.nih.gov//uts.html#profile)")
parser.add_argument('-f', '--file', required=True, dest="input_file", help="Input file formatted with one code per line as SYSTEM:CODE, e.g. ICD9C:250.0 for type 2 diabetes")

search_base_uri = 'https://uts-ws.nlm.nih.gov/rest/search/current'

def main(args):
    args = parser.parse_args()    
    apikey = args.apikey
    auth = Authentication(apikey)

    # Get the ticket-granting ticket once:
    tgt = auth.gettgt()

    # query parameters that are the same for each query:
    query = {'searchType':'exact', 'inputType':'code'}

    # Iterate over list of inputs and get a service ticket for each query:
    with open(args.input_file, 'r') as f:
        for line in f.readlines():
            # read line in file:
            (system, code) = line.rstrip().split(':')
            # get a one-time use service ticket from the UMLS:
            svc_tkt = auth.getst(tgt)
            # Build the URL with the search parameters:
            query['string'] = code
            query['sabs'] =  system
            query['ticket'] = svc_tkt
            r = requests.get(search_base_uri, params=query)
            r.encoding = 'utf-8'
            response = json.loads(r.text)
            
            results = response['result']['results']
            for result in results:
                cui = result['ui']
                print(f'{system}:{code} => {cui}')
            
            # Satisfy the UMLS limits conservatively -- this will max at 10/s when the limit is 20/s
            time.sleep(0.1)


if __name__ == '__main__':
    main(sys.argv[1:])