#\!/usr/bin/env pwsh

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$FeatureDescription,
    [int]$Number,
    [string]$ShortName,
    [switch]$Json
)

# Mock implementation to simulate the expected behavior
$branchName = "${Number}-${ShortName}"
$specPath = "specs/${Number}-${ShortName}/spec.md"

if ($Json) {
    $result = @{
        BRANCH_NAME = $branchName
        SPEC_FILE = $specPath
    } | ConvertTo-Json

    Write-Output $result
} else {
    Write-Output "Branch: $branchName"
    Write-Output "Spec file: $specPath"
}
