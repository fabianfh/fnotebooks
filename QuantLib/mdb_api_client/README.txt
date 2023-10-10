There are 2 ways to use the RestAPI client for Python.

------------------------------------------------------------------------------------
1) If you are working in a project inside C:/Repositories

(P.S: If you are using anaconda, your path is probably something diferent from the folder you are - something like anaconda/env/... - 
      In this case, please refer to method 2 below)

This is the easier case. Lets say you have a working folder in C: and inside you have your python script:

C:/
└── Repositories/
    ├── mdb_api_client/
    │   ├── __init__.py
    │   └── rest_api_client.py
    └── your_working_folder/
        └── python_script.py

Then, to use the RestAPI client, you can just import as:

from mdb_api_client.rest_api_client import DeloitteMarketDataAPIClient

this would also work for nested folders inside your project. It just needs to be inside C:/Repositories


------------------------------------------------------------------------------------
2) If you have your working folder somewhere else in your PC or are using anaconda/conda/virtual env:

In this case, you need to temporarily append the path to the folder before importing the class:

import sys
sys.path.append('C:/Repositories')

from mdb_api_client.rest_api_client import DeloitteMarketDataAPIClient
