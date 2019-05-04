#!/usr/bin/python

import requests
import os
import boto.ec2
import sys
import re

build_url = 'http://localhost:8080/job/ami-creation/24/'
jenkins_base_url = 'http://localhost:8080/'
ami_profile_name = os.environ['AMI_PROFILE_NAME']
jenkins_auth_user = 'packer'
jenkins_auth_password = 'packer'
jenkins_crumb_header_name = ""
jenkins_crumb_header_value = ""
verify_ssl = True
aws_region = os.getenv('AWS_REGION', 'us-east-2')
ec2_cloud_instance = os.getenv('EC2_CLOUD_INSTANCE', 'aws_us-east-2')
output_error_string = os.getenv('OUTPUT_ERROR_STRING', 'Error:')
build_output_text = ""


def get_jenkins_build_output():
    global build_url
    global build_output_text

    if build_output_text:
        return build_output_text

    build_url = build_url.replace('https://', '');
    if not build_url.endswith('/'):
        build_url = '%s/' % build_url
    jenkins_url = 'https://%s:%s@%slogText/progressiveText' % (
            jenkins_auth_user,
            jenkins_auth_password,
            build_url)

    payload = {'start': '1'}
    headers = {jenkins_crumb_header_name: jenkins_crumb_header_value}
    r = requests.get(jenkins_url, verify=verify_ssl,  headers=headers)
    if not r.status_code == 200:
        print 'HTTP POST to Jenkins URL %s resulted in %s' % (jenkins_url, r.status_code)
        print r.headers
        print r.text
        sys.exit(1)

    return r.text

def get_error_lines(build_output):
    retval = ""
    regex = re.compile(r'(.*%s.*)' % output_error_string, re.MULTILINE)
    matches = [m.groups() for m in regex.finditer(build_output)]
    if matches:
        retval = "**************************************************\n"
        retval += " Error string: '%s'\n" % output_error_string
        retval += " Found the following errors in the build output\n"
        retval += "**************************************************\n"
        for m in matches:
            retval += '%s\n' % m[0]
        retval += "**************************************************\n"
    return retval


def main():
	get_jenkins_crumb()
    error_lines = get_error_lines(get_jenkins_build_output())
	
if __name__ == '__main__':
    main()
