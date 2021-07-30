#!/usr/bin/env python3
import sys
import os
import argparse
import json
from sonicapi import SonicAPI


def main():
    print("Welcome to the ZT Restart Script")

    #Parse Arguments from Script
    parser = argparse.ArgumentParser(description="Zero Trust Reset")
    parser.add_argument('-u','--username', \
            help='SonicWall Firewall Admin Username', required=True)
    parser.add_argument('-p','--password', \
            help='SonicWall Firewall Admin Password', required=True)
    parser.add_argument('-f','--fw-hostname', \
            help='SonicWall Firewall Hostname.  \
            Example: nsa.sonicwall.com:4443 (default port:443)', \
            required=True)
    args = vars(parser.parse_args())

    #Create SonicAPI class for firewall
    #Load YAML file for JSON schema
    #Populate authentication credentials
    sonic_os_api = SonicAPI(args["fw_hostname"])
    sonic_os_api.load_yaml("./sonicos_openapi.yml")
    sonic_os_api.set_auth_parameters(args["username"], args["password"], \
            sonic_os_api.AUTH_TYPE_TFA_BEARER)
    print("")
    

    #Login to firewall
    if sonic_os_api.login() == False:
        return
    print("")

    #Send GET request for ZT configuration in DIAG page
    r = sonic_os_api.send_api_request(sonic_os_api.REQUEST_GET, \
            "/diag/advanced/zero-touch/base", None)
    if r.status_code == 200:
        print(r.json())
    else: 
        print("Zero Touch Get Request Failed. HTTP Response Code: + \
                str(r.status_code)")
    print("")

    #Send POST request to reset ZT
    r = sonic_os_api.send_api_request(sonic_os_api.REQUEST_POST, \
            "/diag/advanced/zero-touch/restart", None)
    if r.status_code == 200:
        print(r.json())
        print("Zero Touch Restart Successful")
    else:
        print("Zero Touch Restart Failed.  HTTP Response Code: " + \
                str(r.status_code))
    print("")

    #Logout of firewall
    sonic_os_api.logout()
    print("")

if __name__ == "__main__":
	main()

