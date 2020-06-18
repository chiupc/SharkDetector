$symbol=$args[0]
$counter=$args[1]
$resolution=$args[2]
$event_name="poll-$symbol-event"
$rule_name="poll-$symbol-rule"
$aws_create_rule="aws events put-rule --name $rule_name --schedule-expression 'rate(1 minute)'"
$aws_add_permission="aws lambda add-permission --function-name GenerateCounterCSV --statement-id $event_name --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:ap-southeast-1:662391729800:rule/$rule_name"
$aws_create_targets= "aws events put-targets --rule $rule_name --targets file://targets.json"

echo $aws_create_rule 
try{
    Invoke-Expression $aws_create_rule
}catch{
    Write-Host $_
}
echo $aws_add_permission
try{
    Invoke-Expression $aws_add_permission
}catch{
    Write-Host $_
}

#Replace symbol and counter in target.json to use as input parameter
((Get-Content -path targets.json -Raw) -replace "symbol_param",$symbol -replace "counter_param",$counter -replace "resolution_param",$resolution) | Set-Content -Path targets.json
echo $aws_create_targets
try{
    Invoke-Expression $aws_create_targets
}catch{
    Write-Host $_
}
((Get-Content -path targets.json -Raw) -replace $symbol,'symbol_param' -replace $counter,'counter_param' -replace $resolution,"resolution_param") | Set-Content -Path targets.json
#cmd.exe /c $aws_add_permission