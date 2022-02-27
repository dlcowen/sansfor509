# GCP Command Line Log Collector

The below details how to collect logs from a GCP project via command line.

## Requirements
* An Account with `Private Logs Viewer` permissions
* [gconsole installed](https://cloud.google.com/sdk/docs/install)


## Authenticate to GCP
1. `gcloud init --no-browser`
2. You'll be promoted to select a Project.


## Collect All Logs in a Project
1. Review the Log Buckets in the Project and the age of them
2. `gcloud logging buckets list`
3. Collect all the logs from the Project based on time range.
4. `gcloud logging read 'timestamp<="2022-02-28T00:00:00Z" AND timestamp>="2022-01-01T00:00:00Z"' --format="json" > logs.json`

*Ensure you adjust the dates to be suitable for the time range you require.*


## Collect Logs from a Specific Bucket
1. Review the Log Buckets in the Project and the age of them
2. `gcloud logging buckets list`
3. Collect all the logs from the Project based on time range.
4. `gcloud logging read 'timestamp<="2022-02-28T00:00:00Z" AND timestamp>="2022-01-01T00:00:00Z"' --bucket=<bucket-id> --location=[LOCATION] --format="json" > logs.json`

*Ensure you adjust the dates to be suitable for the time range you require.*


## References
* [Installing the gcloud CLI](https://cloud.google.com/sdk/docs/install)
* [gcloud logging read](https://cloud.google.com/sdk/gcloud/reference/logging/read)
