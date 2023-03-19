# Install the AzTable module if needed
Install-Module AzTable

# Replace the values in these variables with your own:
$storageAccountName = "<Enter your storage account name>"
$storageAccountKey = "<Enter the key for your storage account name>"
$tableName = "WADWindowsEventLogsTable"
$columnName = "RawXml"

# Connect to Azure Storage using the storage account name and key
$context = New-AzStorageContext -StorageAccountName $storageAccountName -StorageAccountKey $storageAccountKey

# Create pointer to WADWindowsEventLogsTable
$storageTable = Get-AzStorageTable -Name $tableName -Context $context
$cloudTable = $storageTable.CloudTable

# Read the table
$entry=Get-AzTableRow -table $cloudTable

# Extract the RawXml column to a text file
$entry.RawXml | out-file "WADWindowsEventLogsTable.xml" -encoding utf8

