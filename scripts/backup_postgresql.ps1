# ============================================================
# Xoradex EduCore - PostgreSQL Automated Backup
# ============================================================

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

$DatabaseName = "xoradex_educore"
$DatabaseUser = "xoradex_app"
$DatabaseHost = "localhost"
$DatabasePort = "5432"

# Number of timestamped backups to retain
$RetentionCount = 14

# Project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Backup directory
$BackupDirectory = Join-Path $ProjectRoot "backups"

# ------------------------------------------------------------
# Prepare backup directory
# ------------------------------------------------------------

if (-not (Test-Path $BackupDirectory)) {

    New-Item `
        -ItemType Directory `
        -Path $BackupDirectory `
        -Force | Out-Null
}

# ------------------------------------------------------------
# Create timestamped backup filename
# ------------------------------------------------------------

$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"

$BackupFile = Join-Path `
    $BackupDirectory `
    "xoradex_educore_$Timestamp.dump"

# ------------------------------------------------------------
# Display backup information
# ------------------------------------------------------------

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Xoradex EduCore PostgreSQL Automated Backup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Database : $DatabaseName"
Write-Host "Host     : $DatabaseHost"
Write-Host "User     : $DatabaseUser"
Write-Host "Backup   : $BackupFile"
Write-Host "Retention: Latest $RetentionCount backups"
Write-Host ""

# ------------------------------------------------------------
# Run PostgreSQL backup
# ------------------------------------------------------------

Write-Host "Creating PostgreSQL backup..." -ForegroundColor Yellow
Write-Host ""

pg_dump `
    -U $DatabaseUser `
    -h $DatabaseHost `
    -p $DatabasePort `
    -d $DatabaseName `
    -F c `
    -f $BackupFile

# ------------------------------------------------------------
# Verify backup file exists
# ------------------------------------------------------------

if (-not (Test-Path $BackupFile)) {

    throw "BACKUP FAILED: Backup file was not created."
}

# ------------------------------------------------------------
# Verify backup file is not empty
# ------------------------------------------------------------

$BackupSize = (Get-Item $BackupFile).Length

if ($BackupSize -le 0) {

    Remove-Item $BackupFile -Force -ErrorAction SilentlyContinue

    throw "BACKUP FAILED: Backup file is empty."
}

# ------------------------------------------------------------
# Backup successful
# ------------------------------------------------------------

Write-Host ""
Write-Host "BACKUP SUCCESSFUL" -ForegroundColor Green
Write-Host ""

Write-Host "File : $BackupFile"
Write-Host "Size : $BackupSize bytes"
Write-Host ""

# ------------------------------------------------------------
# Retention management
# ------------------------------------------------------------

Write-Host "Checking backup retention..." -ForegroundColor Yellow
Write-Host ""

# Only manage automated timestamped backups.
#
# This deliberately excludes:
#   xoradex_educore_postgresql_backup.dump
#
# because that is your manually created backup.

$AutomatedBackups = @(
    Get-ChildItem `
        -Path $BackupDirectory `
        -Filter "xoradex_educore_*.dump" `
        -File |
    Where-Object {
        $_.Name -match '^xoradex_educore_\d{4}-\d{2}-\d{2}_\d{6}\.dump$'
    } |
    Sort-Object LastWriteTime -Descending
)

Write-Host "Automated backups found: $($AutomatedBackups.Count)"
Write-Host ""

# ------------------------------------------------------------
# Delete backups beyond retention count
# ------------------------------------------------------------

if ($AutomatedBackups.Count -gt $RetentionCount) {

    $BackupsToDelete = $AutomatedBackups | Select-Object -Skip $RetentionCount

    foreach ($OldBackup in $BackupsToDelete) {

        Write-Host "Deleting old backup:" -ForegroundColor DarkYellow
        Write-Host "  $($OldBackup.Name)"

        Remove-Item `
            -Path $OldBackup.FullName `
            -Force
    }

    Write-Host ""
    Write-Host "Old backup cleanup completed." -ForegroundColor Green
}
else {

    Write-Host "No old backups need to be deleted." -ForegroundColor Green
}

# ------------------------------------------------------------
# Final backup count
# ------------------------------------------------------------

$RemainingBackups = @(
    Get-ChildItem `
        -Path $BackupDirectory `
        -Filter "xoradex_educore_*.dump" `
        -File |
    Where-Object {
        $_.Name -match '^xoradex_educore_\d{4}-\d{2}-\d{2}_\d{6}\.dump$'
    } |
    Sort-Object LastWriteTime -Descending
)

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host " BACKUP PROCESS COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Current automated backups: $($RemainingBackups.Count)"
Write-Host "Retention limit           : $RetentionCount"
Write-Host ""

Write-Host "Latest backup:"
Write-Host "  $($RemainingBackups[0].Name)"
Write-Host ""

Write-Host "================================================" -ForegroundColor Green
Write-Host ""