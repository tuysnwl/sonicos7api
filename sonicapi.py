#!/usr/bin/env python3
import sys
import os
import requests
import json
import urllib3
import yaml
from collections import OrderedDict
import argparse
from copy import deepcopy

urllib3.disable_warnings()



class SonicAPI:
    REQUEST_GET = 1
    REQUEST_PUT = 2
    REQUEST_POST = 3
    REQUEST_DELETE = 4
    AUTH_TYPE_BASIC_HTTP = 1
    AUTH_TYPE_HTTP_DIGEST = 2
    AUTH_TYPE_TFA_BEARER = 3


    def __send_post_request(self, url, body):
        if body == None:
            if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
                r = requests.post(url, auth=self.auth_basic_http_param, \
                        headers=self.headers, verify=False)
            else:
                r = requests.post(url, headers=self.headers, verify=False)
        else:
            body_str = json.dumps(body)
            if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
                r = requests.post(url, auth=self.auth_basic_http_param, \
                        headers=self.headers, data=body_str, verify=False)
            else:
                r = requests.post(url, headers=self.headers, data=body_str, \
                        verify=False)
        return r

    def __send_get_request(self, url, body):
        if body == None:
            if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
                r = requests.get(url, auth=self.auth_basic_http_param, \
                        headers=self.headers, verify=False)
            else:
                r = requests.get(url, headers=self.headers, verify=False)
        else:
            body_str = json.dumps(body)
            if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
                r = requests.get(url, auth=self.auth_basic_http_param, \
                        headers=self.headers, data=body_str, verify=False)
            else:
                r = requests.get(url, headers=self.headers, data=body_str, \
                        verify=False)
        return r

    def __send_put_request(self, url, body):
        if body == None:
            if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
                r = requests.put(url, auth=self.auth_basic_http_param, \
                        headers=self.headers, verify=False)
            else:
                r = requests.put(url, headers=self.headers, verify=False)
        else:
            body_str = json.dumps(body)
            if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
                r = requests.put(url, auth=self.auth_basic_http_param, \
                        headers=self.headers, data=body_str, verify=False)
            else:
                r = requests.put(url, headers=self.headers, data=body_str, \
                        verify=False)
        return r

    def send_api_request(self, request_type, api_endpoint, body):
        url = self.baseurl + api_endpoint
        if request_type == self.REQUEST_GET:
            print("GET " + url)
            return self.__send_get_request(url, body)
        elif request_type == self.REQUEST_PUT:
            print("PUT " + url)
            return self.__send_put_request(url, body)
        elif request_type == self.REQUEST_POST:
            print("POST " + url)
            return self.__send_post_request(url, body)
        elif request_type == self.REQUEST_DELETE:
            print("DELETE " + url)
            return requests.delete(url, verify=False)
        return

    def login(self):
        if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
            r = self.send_api_request(self.REQUEST_POST, "/auth", None)
            if r.status_code != 200:
                print("Login failed. HTTP Response Code: " + str(r.status_code))
                return False
            else:
                print("Login successful.")
                return True
        elif self.auth_type == self.AUTH_TYPE_HTTP_DIGEST:
            print("HTTP Digest is not yet supported")
        elif self.auth_type == self.AUTH_TYPE_TFA_BEARER:
            tfa = input("Please enter in TFA Code:")
            try:
                tfa_schema = deepcopy(self.sonicos_schema["tfa"]["properties"])
            except ValueError:
                print("No Schemas loaded.  Please load YAML file.")
            tfa_schema["user"] = self.username
            tfa_schema["password"] = self.password
            tfa_schema["tfa"] = tfa
            tfa_schema["override"] = True
            r = self.send_api_request(self.REQUEST_POST, "/tfa", tfa_schema)
            
            if r.status_code != 200:
                print("Login failed. HTTP Response Code: " + str(r.status_code))
                return False
            else:
                response = r.json()
                print(response["status"]["info"])
                print("-----")
                response_info = response["status"]["info"][0]
                print(response_info)
                try:
                    self.bearer_token = deepcopy(response_info['bearer_token'])
                except ValueError:
                    print("Login failed. Bearer token not acquired.")

                print("TFA Login successful.")

                self.headers['Authorization'] = "Bearer " + self.bearer_token  
                return True
        return r.status_code

    def logout(self):
        r = self.send_api_request(self.REQUEST_DELETE, "/auth", None)
        if r.status_code != 200:
            print("Logout failed. HTTP Response Code: " + str(r.status_code))
            return False
        else:
            print("Logout successful.")
            response = r.json()
            return True

    def load_yaml(self, yaml_file):
        #Load YAML file into JSON
        print("Loading "+yaml_file+" YAML file...")
        with open(yaml_file, 'r') as stream:
            try:
                sonicos_json = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        try:
            self.sonicos_schema = sonicos_json['components']['schemas']
        except ValueError:
            print("No Schemas in SonicOS API")
        return

    def set_fw_url(self, hostname):
        self.baseurl = 'https://{0}/api/sonicos'.format(hostname)
        return

    def set_auth_parameters(self, username, password, auth_type):
        self.auth_type = auth_type
        self.username = username
        self.password = password
        if self.auth_type == self.AUTH_TYPE_BASIC_HTTP:
            self.auth_basic_http_param = (self.username, self.password)
        return

    def __init__(self, hostname):
        #Set firewall settings
        self.baseurl = 'https://{0}/api/sonicos'.format(hostname)
        self.headers = OrderedDict([
            ('Accept', 'application/json'),
            ('Content-Type', 'application/json'),
            ('Accept-Encoding', 'application/json'),
            ('Charset', 'UTF-8')])
        
        #Set authentication
        self.auth_type = self.AUTH_TYPE_BASIC_HTTP
        self.username = ""
        self.password = ""
        return

def main():
    print("SonicOS API Python Class\n")
 

if __name__ == "__main__":
	main()

