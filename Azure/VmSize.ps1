# If not already installed, you will need the Az module:
# 	Install-Module –Name Az -AllowClobber
# 	Import-Module Az; Get-Module Az
# Connect to your Azure account and if you have multiple subscriptions, selected the appropriate one:
# 	Connect-AzAccount
# 	Get-AzSubscription
# 	Set-AzContext -Subscription <name of subscription>


# By default get-azlog will only show 1000 events that took place 7 days from the current date/time
# Specify a relevant date range, example: -StartTime 2021-03-31T00:00 -EndTime 2021-04-02T00:00

$results = get-azlog -ResourceProvider "Microsoft.Compute" -DetailedOutput -StartTime 2021-03-31T00:00 -EndTime 2021-04-02T00:00
$results.Properties | foreach {$_} | foreach {
   $contents = $_.content
   if ($contents -and $contents.ContainsKey("responseBody")) {
      $fromjson=($contents.responseBody | ConvertFrom-Json)
      $newobj = New-Object psobject
      $newobj | Add-Member NoteProperty VmId $fromjson.properties.vmId
      $newobj | Add-Member NoteProperty VmSize $fromjson.properties.hardwareprofile.vmsize
      $newobj
      }
}

