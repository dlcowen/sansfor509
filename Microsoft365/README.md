# Initiate Connection with Microsoft 365 Exchange Online
## Conect using Basic Authentication

```
$UserCredential = Get-Credential
$Session = New-PSSession -ConfigurationName Microsoft.Exchange –ConnectionUri https://outlook.office365.com/powershell-liveid/ -Credential $UserCredential -Authentication Basic –AllowRedirection
Import-PSSession $Session –DisableNameChecking –AllowClobber:$true
```

## Connect using MFA
```
Install-Module –Name ExchangeOnlineManagement
Import-Module ExchangeOnlineManagement; Get-Module ExchangeOnlineManagement
Connect-ExchangeOnline –UserPrincipalName <UPN> -ShowProgress $true
```

# Example UAL Searches

## Basic search
`Search-UnifiedAuditLog –StartDate 2020-01-01 –EndDate 2020-02-28`

## Search for all login records
`Search-UnifiedAuditLog –StartDate 2020-01-01 –EndDate 2020-02-28 –Operations UserLoggedIn`

## Search for all login records for a specific user
`Search-UnifiedAuditLog –StartDate 2020-01-01 –EndDate 2020-02-28 –Operations UserLoggedIn -UserIds jvandyne@pymtechlabs.com`

## Search for all failed logins and export to CSV (increase to maximum number of results)
`Search-UnifiedAuditLog –StartDate 2020-01-01 –EndDate 2020-02-28 –Operations UserLoginFailed -ResultSize 5000 –SessionCommand ReturnLargeSet | Export-Csv –Path “c:\data\userloginfailed.csv”`

## Search for all events and return results as JSON
`Search-UnifiedAuditLog –StartDate 2020-01-01 –EndDate 2020-02-28 –SessionCommand ReturnLargeSet -ResultSize 5000 | Select-Object –ExpandProperty AuditData`

## Verify that mailbox auditing is on
`Get-OrganizationConfig | Format-List AuditDisabled`

## Check specific mailbox (admin in this example) auditing configuration
`Get-Mailbox –Identity admin | Select-Object –ExpandProperty AuditOwner`
