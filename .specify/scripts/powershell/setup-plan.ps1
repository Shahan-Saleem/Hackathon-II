#\!/usr/bin/env pwsh

param([switch]$Json)

if ($Json) {
    $result = @{
        FEATURE_SPEC = "specs/1-todo-app/spec.md"
        IMPL_PLAN = "specs/1-todo-app/plan.md"
        SPECS_DIR = "specs/1-todo-app"
        BRANCH = "1-todo-app"
    } | ConvertTo-Json

    Write-Output $result
} else {
    Write-Output "FEATURE_SPEC=specs/1-todo-app/spec.md"
    Write-Output "IMPL_PLAN=specs/1-todo-app/plan.md"
    Write-Output "SPECS_DIR=specs/1-todo-app"
    Write-Output "BRANCH=1-todo-app"
}
