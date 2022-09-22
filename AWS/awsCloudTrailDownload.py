#!/usr/bin/env python3
# AWS Default Cloudtrail Download script for FOR509
# This script will dump the last 90 days of CloudTrail logs from the AWS maintained trail
# For org created trails in buckets you will need to download that bucket
# V2 of this script now iterates through all regions
# V3 of this script now uses multiprocess to download from all regions at the same time
# Copyright: David Cowen 2022

from __future__ import print_function
import boto3, argparse, os, sys, json, time, random, string, gzip, multiprocessing, curses
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from multiprocessing import Process, TimeoutError, parent_process, Pipe

def regionDownload(access_key_id, secret_access_key, session_token, region_name, conn):

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

    for page in page_iterator:
        filename = '%s_CloudTrail_%s_%s_%s.json.gz' % (account_id, region_name, timestamp,total_logs)
        cloudTraillogs = gzip.open(filename, 'w')
        data={}
        data['Records'] = []

        if len(page['Events']) == 0:
            continue


        

        for event in page['Events']:
            data['Records'].append(json.loads(event['CloudTrailEvent']))

        cloudTraillogs.write(json.dumps(data).encode('utf-8'))
        
        total_logs = total_logs + len(page['Events'])
        #print('\rTotal Logs downloaded: %s' % (total_logs), end='',flush=True)
        conn.put([region_name, total_logs])
        cloudTraillogs.close()
        try:
            token_filename = region_name + 'token'
            token_file = open(token_filename,'w')
            token_file.write(page['NextToken'])
            StartingToken = page['NextToken']
        except KeyError:
            continue

    

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

    stdscr = curses.initscr()
    stdscr.border(0)
    stdscr.addstr(0, 0, 'Downloading AWS CloudTrail logs from All Regions', curses.A_BOLD)
    stdscr.addstr(1, 1, 'Press q to quit', curses.A_BOLD)
    stdscr.nodelay(1)
    curses.cbreak()
    

    client = boto3.client(
        'ec2',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name = 'us-east-1'
        )
    total_logs = 0
    regions = client.describe_regions()
    regionindex = {}
    region_count = 2
    n = multiprocessing.Queue()

    for region in regions['Regions']:
        region_name = region['RegionName']
        regionindex[region_name]=region_count
        Process(target=regionDownload, args=(access_key_id,secret_access_key, session_token, region_name, n)).start()
        stdscr.addstr(int(regionindex[region_name]), 1, region_name+': 0', curses.A_NORMAL)
        region_count = region_count + 1

    
    while n:
        (region_name, log_count) = n.get()
        stdscr.addstr(int(regionindex[region_name]), 1, region_name+': '+ str(log_count), curses.A_NORMAL)
        if stdscr.getch() == ord('q'):
            curses.endwin()
            sys.exit()
    curses.endwin()
    sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script will fetch the last 90 days of cloudtrail logs.')
    parser.add_argument('--access-key-id', required=False, default=None, help='The AWS access key ID to use for authentication.')
    parser.add_argument('--secret-key', required=False, default=None, help='The AWS secret access key to use for authentication.')
    parser.add_argument('--session-token', required=False, default=None, help='The AWS session token to use for authentication, if there is one.')

    args = parser.parse_args()
    main(args)
