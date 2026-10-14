# Link Claude Code config from this repo into ~\.claude (Windows).
# Needs Developer Mode on, or an elevated shell, to create symlinks.
$src = $PSScriptRoot
$dst = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$stamp = Get-Date -Format yyyyMMddHHmmss

function Link($from, $to) {
    $item = Get-Item $to -Force -ErrorAction SilentlyContinue
    if ($item -and $item.LinkType -eq "SymbolicLink" -and $item.Target -eq $from) { Write-Host "ok      $to"; return }
    if ($item) { Move-Item $to "$to.bak.$stamp"; Write-Host "backup  $to" }
    New-Item -ItemType SymbolicLink -Path $to -Target $from | Out-Null
    Write-Host "linked  $to"
}

New-Item -ItemType Directory -Force (Join-Path $dst "skills") | Out-Null
Link (Join-Path $src "CLAUDE.md")     (Join-Path $dst "CLAUDE.md")
Link (Join-Path $src "settings.json") (Join-Path $dst "settings.json")
Get-ChildItem (Join-Path $src "skills") -Directory | ForEach-Object {
    Link $_.FullName (Join-Path $dst "skills\$($_.Name)")
}
