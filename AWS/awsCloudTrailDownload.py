#!/usr/bin/env python3
# AWS Default Cloudtrail Download script for FOR509
# This script will dump the last 90 days of CloudTrail logs from the AWS maintained trail
# For org created trails in buckets you will need to download that bucket
# V2 of this script now iterates through all regions
# V3 of this script now uses multiprocess to download from all regions at the same time
# Copyright: David Cowen 2022

from __future__ import print_function
import boto3, argparse, os, sys, json, time, random, string, gzip, multiprocessing
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from multiprocessing import Process, TimeoutError, parent_process, Pipe

def regionDownload(access_key_id, secret_access_key, session_token, region_name,random_source, conn):
    print('\n\rCurrent region: %s' % (region_name))

    accountid_client = boto3.client(
        'sts',
        aws_access_key_id = access_key_id,
        aws_secret_access_key = secret_access_key,
        aws_session_token = session_token,
        region_name = region_name)

    client = boto3.client(
        'cloudtrail',
        aws_access_key_id = access_key_id,
        aws_secret_access_key = secret_access_key,
        aws_session_token = session_token,
        region_name = region_name)

    paginator = client.get_paginator('lookup_events')

    StartingToken = None
    total_logs = 0
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%SZ')
    account_id = accountid_client.get_caller_identity()["Account"]

    page_iterator = paginator.paginate(
        LookupAttributes=[],
        PaginationConfig={ 'PageSize':50, 'StartingToken':StartingToken })
    filename = '%s_CloudTrail_%s_%s.json.gz' % (account_id, region_name, timestamp)
    cloudTraillogs = gzip.open(filename, 'w')
    for page in page_iterator:

        data={}
        data['Records'] = []

        if len(page['Events']) == 0:
            continue

        #unique_string = ''
        #for i in range(16):
        #    unique_string += random.choice(random_source)

        

        for event in page['Events']:
            data['Records'].append(json.loads(event['CloudTrailEvent']))

        cloudTraillogs.write(json.dumps(data).encode('utf-8'))
        #cloudTraillogs.close()
        total_logs = total_logs + len(page['Events'])
        #print('\rTotal Logs downloaded: %s' % (total_logs), end='',flush=True)
        conn.put([region_name, total_logs])

        try:
            token_file = open('token','w')
            token_file.write(page['NextToken'])
            StartingToken = page['NextToken']
        except KeyError:
            continue

def main(args):
    access_key_id = args.access_key_id
    secret_access_key = args.secret_key
    session_token = args.session_token

    random_source = string.ascii_letters + string.digits

    if args.access_key_id is None or args.secret_key is None:
        print('IAM keys not passed in as arguments, enter them below:')
        access_key_id = input('  Access Key ID: ')
        secret_access_key = input('  Secret Access Key: ')
        session_token = input('  Session Token (Leave blank if none): ')
        if session_token.strip() == '':
            session_token = None

    # Begin permissions enumeration


    client = boto3.client(
        'ec2',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name = 'us-east-1'
        )
    total_logs = 0
    regions = client.describe_regions()
    
    #parent_conn = ()
    
    n = multiprocessing.Queue()

    for region in regions['Regions']:
        region_name = region['RegionName']
        #parent_conn[region_name], child_conn = Pipe()
        Process(target=regionDownload, args=(access_key_id,secret_access_key, session_token, region_name,random_source, n)).start()

    
    while n:
        print(n.get())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script will fetch the last 90 days of cloudtrail logs.')
    parser.add_argument('--access-key-id', required=False, default=None, help='The AWS access key ID to use for authentication.')
    parser.add_argument('--secret-key', required=False, default=None, help='The AWS secret access key to use for authentication.')
    parser.add_argument('--session-token', required=False, default=None, help='The AWS session token to use for authentication, if there is one.')

    args = parser.parse_args()
    main(args)
