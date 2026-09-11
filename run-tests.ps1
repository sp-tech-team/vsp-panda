param(
    [string]$BaseUrl = "https://vsp-panda.streamlit.app/",
    [string]$TestPath = ""
)

$ErrorActionPreference = "Stop"

$env:BASE_URL = $BaseUrl
$env:CI = "false"

Push-Location $PSScriptRoot
try {
    python -m pytest --rootdir=test_automation test_automation/$TestPath
}
finally {
    Pop-Location
}