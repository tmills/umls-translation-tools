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
parser.add_argument('-f', '--file', required=True, dest="input_file", help="Input file formatted with one code per line, e.g. C0004057 for aspirin")

search_base_uri = 'https://uts-ws.nlm.nih.gov/rest/content/current/CUI/%s/atoms'

def get_uri(cui):
    return search_base_uri % cui

def main(args):
    args = parser.parse_args()    
    apikey = args.apikey
    auth = Authentication(apikey)

    # Get the ticket-granting ticket once:
    tgt = auth.gettgt()

    # query parameters that are the same for each query:
    query = {'pageSize' : 100}

    # Iterate over list of inputs and get a service ticket for each query:
    input_codes = 0
    icd_exists = 0
    no_icd = 0
    with open(args.input_file, 'r') as f:
        for line in f.readlines():
            input_codes += 1
            # read line in file:
            code = line.rstrip()
            # get a one-time use service ticket from the UMLS:
            page_count = 1
            page_num = 0
            this_icd_exists = False

            while page_num < page_count:
                page_num += 1
                # Build the URL with the search parameters:
                svc_tkt = auth.getst(tgt)
                query['ticket'] = svc_tkt
                query['pageNumber'] = page_num
                r = requests.get(get_uri(code), params=query)
                # Just to make sure we always take a break, do it right after each request
                time.sleep(0.1)
                r.encoding = 'utf-8'
                response = json.loads(r.text)

                for atom in response['result']:
                    src = atom['rootSource']
                    if 'ICD' in src:
                        print("Found an ICD code for this CUI: %s %s" % (src, code))
                        icd_exists += 1
                        this_icd_exists = True
                        break

                if this_icd_exists:
                    break
                pageCount = response['pageCount']

            if not this_icd_exists:
                no_icd += 1
                print("No ICD code for this CUI: %s" % (code))

            #results = response['result']['results']
            #for result in results:
            #    cui = result['ui']
            #    print(f':{code} => {cui}')
            
            # Satisfy the UMLS limits conservatively -- this will max at 10/s when the limit is 20/s


if __name__ == '__main__':
    main(sys.argv[1:])
