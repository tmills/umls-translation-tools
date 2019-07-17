# umls-translation-tools

## Task: Converting from some coding system into CUIs:
Step 1: Obtain your UMLS api key following step 1 here: https://documentation.uts.nlm.nih.gov/rest/authentication.html
Step 2: Run ```python get_cuis_for_icd.py -k <api key> -f test_input.txt``` where ```<api key>``` is replaced with the key you obtained in Step 1.
Step 3: Replace ```test_input.txt``` with your own file with similar formatting.
