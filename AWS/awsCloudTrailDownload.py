#!/usr/bin/env python3
# AWS Default Cloudtrail Download script for FOR509
# This script will dump the last 90 days of CloudTrail logs from the AWS maintained trail
# For org created trails in buckets you will need to download that bucket
# V2 of this script now iterates through all regions
# Copyright: David Cowen 2022

from __future__ import print_function
import boto3, argparse, os, sys, json, time
from botocore.exceptions import ClientError

def main(args):
    access_key_id = args.access_key_id
    secret_access_key = args.secret_key
    session_token = args.session_token

    if args.access_key_id is None or args.secret_key is None:
        print('IAM keys not passed in as arguments, enter them below:')
        access_key_id = input('  Access Key ID: ')
        secret_access_key = input('  Secret Access Key: ')
        session_token = input('  Session Token (Leave blank if none): ')
        if session_token.strip() == '':
            session_token = None

    # Begin permissions enumeration


    cloudTraillogs = open("90days.json","w")
    client = boto3.client(
        'ec2',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        )
    total_logs = 0
    regions = client.describe_regions()
    
    for r in regions['Regions']:
        print("Current region:",r['RegionName'])
        client = boto3.client(
        'cloudtrail',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=r['RegionName']
        )
        paginator = client.get_paginator('lookup_events')

        StartingToken = None
        
        
        page_iterator = paginator.paginate(
            LookupAttributes=[],
            PaginationConfig={'PageSize':50, 'StartingToken':StartingToken })
        for page in page_iterator:
            for event in page["Events"]:
                cloudTraillogs.write(str(event))
                
                
            try:
                token_file = open("token","w") 
                token_file.write(page["NextToken"]) 
                StartingToken = page["NextToken"]
            except KeyError:
                continue
            print("Total Logs downloaded: ",total_logs)
            total_logs = total_logs +50


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script will fetch the last 90 days of cloudtrail logs.')
    parser.add_argument('--access-key-id', required=False, default=None, help='The AWS access key ID to use for authentication.')
    parser.add_argument('--secret-key', required=False, default=None, help='The AWS secret access key to use for authentication.')
    parser.add_argument('--session-token', required=False, default=None, help='The AWS session token to use for authentication, if there is one.')

    args = parser.parse_args()
    main(args)
