
Begin {

    [String]$urlPublicApi = "https://trustpv.goantares.uno/public/api/v3/"
    [String]$urlAnalyticsApi = "https://trustpv.goantares.uno/public/analytics/v3/"
    [String]$apiKey = "471a9bb6-d629-495f-b489-f8a2ab888332"
    [String]$apiSecret = "d96cd920-bf80-4ccc-beec-330860114a99"

    $contentJson = "application/json; charset=utf-8"
    $base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $apiKey, $apiSecret)))
    $headers = @{
        Authorization = ("Basic $base64AuthInfo")
    }

    function AntaresApi_Get {    
        param(
            [Parameter(Mandatory)]$url
        )
        $result = Invoke-RestMethod -Headers $headers $url
        return $result
    }
      
    function AntaresApi_Delete {    
        param(
            [Parameter(Mandatory)]$url
        )
        $result = Invoke-RestMethod -Method DELETE -ContentType $contentJson -Headers $headers  $url
        return $result
    }


    try {
        #create new ticket
        $Tickets = AntaresApi_Get "$($urlPublicApi)Tickets?`$filter=HelpdeskId eq ecddfa70-b0d3-406e-9cf0-b5880429bafb"

        foreach($t in $tickets) {
            AntaresApi_Delete "$($urlPublicApi)Tickets/$($t.Id)" 
        }            
    }
    catch {
        Write-Host ($ticket |  ConvertTo-Json)
        Write-Error $_.Exception.Message
    }

}