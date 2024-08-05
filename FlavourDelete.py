import requests
import json
import xml.etree.ElementTree as ET
import hashlib
# Data from Kaltura & Session
base_url = 'https://www.kaltura.com/api_v3/'
KString = input("Provide the KS with Admin priviledges: ")
# Service, action, and parameters
CSVList = input("Provide the entry list separated by commas: ")
entryList = CSVList.split(',')
CSVFlavor = input("Provide the flavour IDs separated by commas: ")
flavorDeleteList = CSVFlavor.split(',')
id_flavor_dict = {}

#Iterate on the entry list
for entryID in entryList:

    # List flavours for entry
    list_url = f'{base_url}service/flavorAsset/action/getFlavorAssetsWithParams'
    list_payload = {
        "ks": f'{KString}',
        "entryId": entryID
    }
    listResp = requests.post(list_url, data=list_payload)
    #print(listResp.content)


    # Parse the XML result
    root = ET.fromstring(listResp.text)
    for item in root.findall(".//flavorAsset"):
        id_element = item.find(".//id")
        flavorParam = item.find(".//flavorParamsId")
        if id_element is not None and flavorParam is not None:
            id_flavor_dict[int(flavorParam.text.strip())] = id_element.text.strip()
    #print(id_flavor_dict)

    for flavor in flavorDeleteList:
        try:
            del_url = f'{base_url}service/flavorAsset/action/delete'
            del_payload = {
                "ks": f'{KString}',
                "id": id_flavor_dict[flavor]
            }
            delResp = requests.post(del_url, data=del_payload)
            print(flavor,delResp,sep=':',end='\n')
        except KeyError:
            print(flavor,'does not exists for entry:',entryID,sep=' ',end='\n')

