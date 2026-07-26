# IRIS - AI Command Terminal
# Persistent console: every command the AI runs (via the run_command MCP
# tool) executes HERE, in this one visible window, instead of popping a new
# window per command. Jobs are dropped as .job files in iris_data/cmd_queue
# and picked up by the loop below; results are written back as .result files.

$Root = Split-Path -Parent $PSScriptRoot
$Queue = Join-Path $Root "iris_data\cmd_queue"
New-Item -ItemType Directory -Force -Path $Queue | Out-Null

$host.UI.RawUI.WindowTitle = "IRIS - AI Command Terminal"
Clear-Host
Write-Host ""
Write-Host "     #####################################" -ForegroundColor Cyan
Write-Host "     ###                                 ###" -ForegroundColor Cyan
Write-Host "     ###          I   R   I   S             ###" -ForegroundColor Cyan
Write-Host "     ###                                 ###" -ForegroundColor Cyan
Write-Host "     #####################################" -ForegroundColor Cyan
Write-Host ""
Write-Host "              AI COMMAND TERMINAL" -ForegroundColor DarkCyan
Write-Host "        every backend command Iris runs shows up here" -ForegroundColor DarkGray
Write-Host ""

while ($true) {
    $jobs = Get-ChildItem -Path $Queue -Filter "*.job" -ErrorAction SilentlyContinue | Sort-Object CreationTime
    foreach ($job in $jobs) {
        $id = $job.BaseName
        $cmd = Get-Content -Raw -Path $job.FullName -ErrorAction SilentlyContinue
        Remove-Item -Force -Path $job.FullName -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }

        Write-Host ">> $cmd" -ForegroundColor Yellow
        $resultPath = Join-Path $Queue "$id.result"
        try {
            $output = Invoke-Expression $cmd 2>&1 | Out-String
            $rc = if ($LASTEXITCODE) { $LASTEXITCODE } else { 0 }
        } catch {
            $output = $_.Exception.Message
            $rc = 1
        }
        Write-Host $output
        Write-Host "[exit $rc]" -ForegroundColor DarkGray
        Write-Host ""
        Set-Content -Path $resultPath -Value ("$rc`n$output") -Encoding utf8
    }
    Start-Sleep -Milliseconds 300
}
