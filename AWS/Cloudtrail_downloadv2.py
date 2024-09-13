#!/usr/bin/env python3
# AWS CloudTrail Download Script with auto-resume, event tracking, token management, and directory output for logs
# Supports resumable downloads, AWS credentials from credentials file, progress tracking, and cross-platform compatibility.

from __future__ import print_function
import boto3, argparse, os, sys, json, time, gzip, multiprocessing, curses, platform
from botocore.exceptions import ClientError
from datetime import datetime

def regionDownload(session_params, region_name, log_directory, queue):
    """
    Downloads CloudTrail logs for a specific region and stores the pagination token and the number of events already downloaded for resuming if interrupted.
    Saves logs to the specified directory.
    """
    session = boto3.Session(
        aws_access_key_id=session_params['aws_access_key_id'],
        aws_secret_access_key=session_params['aws_secret_access_key'],
        aws_session_token=session_params['aws_session_token'],
        region_name=region_name
    )

    client = session.client('cloudtrail', region_name=region_name)
    paginator = client.get_paginator('lookup_events')
    token_filename = os.path.join(log_directory, f'{region_name}_resume.json')
    StartingToken = None
    total_logs = 0
    is_resumed = False  # Flag to check if this is a resumed download

    # Load the token and event count from the file if it exists (to resume)
    if os.path.exists(token_filename):
        try:
            if os.path.getsize(token_filename) > 0:  # Check if the file is not empty
                with open(token_filename, 'r') as f:
                    token_data = json.load(f)
                    StartingToken = token_data.get('NextToken')
                    total_logs = token_data.get('DownloadedEvents', 0)
                    is_resumed = True  # Mark as resumed
            else:
                # If the file is empty, mark as completed
                queue.put([region_name, 'done', is_resumed])
                return
        except (json.JSONDecodeError, KeyError):
            # If the JSON is invalid, mark the region as done and log an error
            queue.put([region_name, 'done', is_resumed])
            return

    timestamp = datetime.now().strftime('%Y%m%dT%H%M%SZ')
    account_id = session.client('sts', region_name=region_name).get_caller_identity()["Account"]

    # Fetch logs using pagination
    page_iterator = paginator.paginate(
        LookupAttributes=[],
        PaginationConfig={'PageSize': 50, 'StartingToken': StartingToken}
    )

    for page in page_iterator:
        filename = os.path.join(log_directory, f'{account_id}_CloudTrail_{region_name}_{timestamp}_{total_logs}.json.gz')
        with gzip.open(filename, 'w') as cloudTrail_logs:
            data = {'Records': []}
            
            if len(page['Events']) == 0:
                continue

            # Collect logs from the events
            for event in page['Events']:
                data['Records'].append(json.loads(event['CloudTrailEvent']))

            cloudTrail_logs.write(json.dumps(data).encode('utf-8'))
            total_logs += len(page['Events'])
            queue.put([region_name, total_logs, is_resumed])  # Send the log count and resume status to the main process

        # Save token and downloaded event count for resuming
        try:
            with open(token_filename, 'w') as token_file:
                token_data = {
                    'NextToken': page['NextToken'],
                    'DownloadedEvents': total_logs
                }
                json.dump(token_data, token_file)
            StartingToken = page['NextToken']
        except KeyError:
            pass  # No more pages

    # Signal that the region download is complete
    queue.put([region_name, 'done', is_resumed])
    queue.close()

def remove_all_token_files(regions, log_directory):
    """
    Removes all resume token files for the regions after the entire process is complete.
    Only removes files if all regions are done.
    """
    for region in regions:
        token_filename = os.path.join(log_directory, f'{region}_resume.json')
        if os.path.exists(token_filename):
            os.remove(token_filename)

def all_regions_done(completed_regions, total_regions):
    """
    Check if all regions are done.
    """
    return len(completed_regions) == total_regions

def main(args):
    """
    Main function to initiate the downloading of CloudTrail logs from all regions and save them to the specified directory.
    Automatically resumes from token files if present and deletes token files once all regions are done.
    """

    # Create a session dictionary that can be passed to processes (since boto3 session objects are not pickleable)
    session_params = {
        'aws_access_key_id': args.access_key_id,
        'aws_secret_access_key': args.secret_key,
        'aws_session_token': args.session_token
    }

    if not args.access_key_id and not args.secret_key:
        # Load credentials from the AWS credentials file
        session = boto3.Session(profile_name=args.profile)
        credentials = session.get_credentials().get_frozen_credentials()
        session_params['aws_access_key_id'] = credentials.access_key
        session_params['aws_secret_access_key'] = credentials.secret_key
        session_params['aws_session_token'] = credentials.token

    # Create the output directory if it doesn't exist
    log_directory = args.output_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    stdscr = curses.initscr()  # Initialize curses screen
    try:
        stdscr.border(0)
        stdscr.addstr(0, 0, 'Downloading AWS CloudTrail logs from All Regions', curses.A_BOLD)
        stdscr.addstr(1, 1, 'Press q to quit', curses.A_BOLD)
        stdscr.nodelay(1)
        curses.cbreak()

        # Retrieve AWS regions
        ec2_client = boto3.client('ec2', aws_access_key_id=session_params['aws_access_key_id'],
                                  aws_secret_access_key=session_params['aws_secret_access_key'],
                                  aws_session_token=session_params['aws_session_token'],
                                  region_name='us-east-1')

        regions = ec2_client.describe_regions()
        regionindex = {}
        region_count = 2
        regions_done = 0
        log_queue = multiprocessing.Queue()

        start_time = time.time()  # Start time for calculating the total run time

        processes = []
        completed_regions = []  # List of completed regions

        # Start processes to download logs for each region
        for region in regions['Regions']:
            region_name = region['RegionName']
            stdscr.addstr(region_count, 1, f'{region_name}: 0 events', curses.A_NORMAL)
            regionindex[region_name] = region_count

            # Check if this region has a completed token file
            token_filename = os.path.join(log_directory, f'{region_name}_resume.json')
            if os.path.exists(token_filename):
                with open(token_filename, 'r') as f:
                    try:
                        token_data = json.load(f)
                        if 'NextToken' not in token_data:  # If there is no next token, this region is complete
                            stdscr.addstr(region_count, 1, ' ' * 50)  # Clear previous content
                            stdscr.addstr(region_count, 1, f'{region_name}: DONE', curses.A_BOLD)
                            completed_regions.append(region_name)
                            regions_done += 1
                            region_count += 1
                            continue
                    except (json.JSONDecodeError, KeyError):
                        stdscr.addstr(region_count, 1, ' ' * 50)  # Clear previous content
                        stdscr.addstr(region_count, 1, f'{region_name}: DONE', curses.A_BOLD)
                        completed_regions.append(region_name)
                        regions_done += 1
                        region_count += 1
                        continue

            # Start a new process for regions that are not marked as done
            process = multiprocessing.Process(target=regionDownload, args=(session_params, region_name, log_directory, log_queue))
            processes.append(process)
            process.start()
            region_count += 1

        # Monitor the progress of the downloads
        total_downloaded = 0
        while regions_done < region_count - 2:
            region_name, log_count, is_resumed = log_queue.get()
            if log_count == "done":
                regions_done += 1
                stdscr.addstr(int(regionindex[region_name]), 1, ' ' * 50)  # Clear previous content
                stdscr.addstr(int(regionindex[region_name]), 1, f'{region_name}: DONE', curses.A_BOLD)
                completed_regions.append(region_name)
            else:
                stdscr.addstr(int(regionindex[region_name]), 1, f'{region_name}: {log_count} events', curses.A_NORMAL)
                total_downloaded += log_count

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            if is_resumed:
                stdscr.addstr(0, 50, f'RESUMED DOWNLOAD - Elapsed: {int(elapsed_time)}s')
            else:
                stdscr.addstr(0, 50, f'Elapsed: {int(elapsed_time)}s')

            if stdscr.getch() == ord('q'):
                # Cleanup and exit
                stdscr.addstr(0, 50, "Exiting...")
                break

        # Terminate all running processes
        for process in processes:
            process.terminate()
            process.join()

    finally:
        curses.endwin()  # Ensure curses cleans up the terminal state even if an error occurs

    # Only remove token files if all regions are done
    if all_regions_done(completed_regions, len(regions['Regions'])):
        remove_all_token_files([region['RegionName'] for region in regions['Regions']], log_directory)

    total_time = time.time() - start_time
    print(f'Total logs downloaded: {total_downloaded}. Total time: {int(total_time)} seconds.')
    sys.exit(0)

if __name__ == '__main__':
    # Ensure the 'spawn' method is used for multiprocessing on Windows
    if platform.system() == 'Windows':
        multiprocessing.set_start_method('spawn')

    parser = argparse.ArgumentParser(description='This script will fetch the last 90 days of CloudTrail logs.')
    parser.add_argument('--access-key-id', required=False, default=None, help='The AWS access key ID to use for authentication.')
    parser.add_argument('--secret-key', required=False, default=None, help='The AWS secret access key to use for authentication.')
    parser.add_argument('--session-token', required=False, default=None, help='The AWS session token to use for authentication, if there is one.')
    parser.add_argument('--profile', required=False, default='default', help='The AWS profile name to use from the credentials file.')
    parser.add_argument('--output-directory', required=True, help='Directory to save CloudTrail logs.')

    args = parser.parse_args()
    main(args)
