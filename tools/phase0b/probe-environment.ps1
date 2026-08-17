[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'

function Find-CommandPath([string] $Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return $null
    }
    return $command.Source
}

$currentVersion = Get-ItemProperty `
    'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$vswhere = 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe'
$visualStudio = @()
if (Test-Path -LiteralPath $vswhere) {
    $visualStudio = (& $vswhere -all -products * -format json | ConvertFrom-Json)
}

$commandNames = @(
    'dotnet', 'java', 'javac', 'gradle', 'adb', 'emulator', 'sdkmanager',
    'avdmanager', 'flutter', 'dart', 'rustc', 'cargo', 'node', 'npm',
    'makeappx', 'signtool'
)
$commands = [ordered]@{}
foreach ($name in $commandNames) {
    $commands[$name] = Find-CommandPath $name
}

$androidCandidates = @(
    "$env:LOCALAPPDATA\Android\Sdk",
    "$env:ProgramFiles\Android\Android Studio",
    "${env:ProgramFiles(x86)}\Android\Android Studio",
    'C:\Program Files\dotnet\packs\Microsoft.Android.Sdk.Windows',
    'C:\Program Files\dotnet\packs\Microsoft.Maui.Sdk'
)
$androidPaths = [ordered]@{}
foreach ($candidate in $androidCandidates) {
    $androidPaths[$candidate] = Test-Path -LiteralPath $candidate
}

$adbDevices = @()
if ($null -ne $commands['adb']) {
    $adbDevices = @(& $commands['adb'] devices -l 2>&1)
}

$avds = @()
if ($null -ne $commands['emulator']) {
    $avds = @(& $commands['emulator'] -list-avds 2>&1)
}
$androidUsbDevices = @(
    & pnputil.exe /enum-devices /connected /class AndroidUsbDeviceClass 2>&1 |
        ForEach-Object { $_.ToString() }
)

$dotnetInfo = @(& dotnet --info 2>&1 | ForEach-Object { $_.ToString() })
$dotnetWorkloads = @(& dotnet workload list 2>&1 | ForEach-Object { $_.ToString() })
$null = & dotnet new list maui 2>$null
$mauiTemplateAvailable = $LASTEXITCODE -eq 0

$evidence = [ordered]@{
    generated_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
    os = [ordered]@{
        runtime_version = [System.Environment]::OSVersion.VersionString
        display_version = $currentVersion.DisplayVersion
        build = $currentVersion.CurrentBuildNumber
        ubr = $currentVersion.UBR
        edition = $currentVersion.EditionID
        process_architecture = [System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture.ToString()
    }
    visual_studio = @($visualStudio | ForEach-Object {
        [ordered]@{
            display_name = $_.displayName
            installation_version = $_.installationVersion
            installation_path = $_.installationPath
        }
    })
    commands = $commands
    android_environment = [ordered]@{
        android_home_set = [bool]$env:ANDROID_HOME
        android_sdk_root_set = [bool]$env:ANDROID_SDK_ROOT
        candidate_paths = $androidPaths
        adb_devices = $adbDevices
        emulator_avds = $avds
        connected_android_usb_class = $androidUsbDevices
    }
    dotnet = [ordered]@{
        info = $dotnetInfo
        workloads = $dotnetWorkloads
        maui_template_available = $mauiTemplateAvailable
    }
}

$evidence | ConvertTo-Json -Depth 8
