# Google Workspace Log Collection
**README is under construction...**

Service account credentials must be created to be used with this script. Once the credentials are created, update config.json with the following information:

1. The location of the JSON file containing the Service Account credentials
1. The principal name for the service account
1. The output folder where you would like all of the JSON files written to that will be collected via the script. 

e.g.
```
{
    "creds_path": "./credentials.json",
    "delegated_creds": "user@domain.com",
    "output_path": "."
}
```

Execute the script with the following command: 

```python3 gws-get-logs.py```

Additional arguments can also be supplied if you wish to change the default script behaviour. Help for those arguments can be obtained by running the following command:

```python3 gws-get-logs.py --help```

```
usage: gws-get-logs.py [-h] [--config CONFIG] [--creds-path CREDS_PATH] [--delegated-creds DELEGATED_CREDS]
                       [--output-path OUTPUT_PATH] [--apps APPS] [--from-date FROM_DATE] [--update] [--overwrite]
                       [--quiet] [--debug]

This script will fetch Google Workspace logs.

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Configuration file containing required arguments
  --creds-path CREDS_PATH
                        .json credential file for the service account.
  --delegated-creds DELEGATED_CREDS
                        Principal name of the service account
  --output-path OUTPUT_PATH, -o OUTPUT_PATH
                        Folder to save downloaded logs
  --apps APPS, -a APPS  Comma separated list of applications whose logs will be downloaded. Or 'all' to attempt to
                        download all available logs
  --from-date FROM_DATE
                        Only capture log entries from the specified date (suggest using yyyy-mm-dd format, although
                        other formats may be accepted.).
  --update, -u          Update existing log files (if present). This will only save new log records.
  --overwrite           Overwrite existing log files (if present), with all available (or requested) log records.
  --quiet, -q           Prevent all output except errors
  --debug, -v           Show debug/verbose output.
  ```