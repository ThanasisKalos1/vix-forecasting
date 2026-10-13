param([switch]$Download)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$raw = Join-Path $root 'data/raw/VIX_History.csv'
$processed = Join-Path $root 'data/processed/vix_daily_2015_2025.csv'
$url = 'https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv'
New-Item -ItemType Directory -Force -Path (Split-Path $raw), (Split-Path $processed) | Out-Null
if ($Download) {
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $raw
}
if (!(Test-Path -LiteralPath $raw)) { throw 'Raw file missing. Run with -Download first.' }
$culture = [Globalization.CultureInfo]::InvariantCulture
$source = @(Import-Csv -LiteralPath $raw)
if (!$source.Count -or !($source[0].PSObject.Properties.Name -contains 'CLOSE')) { throw 'Unexpected CSV schema.' }
$rows = @(foreach ($row in $source) {
    $date = [datetime]::ParseExact($row.DATE, 'MM/dd/yyyy', $culture)
    if ($date.Year -ge 2015 -and $date.Year -le 2025) {
        $close = [double]::Parse($row.CLOSE, $culture)
        if ([double]::IsNaN($close) -or [double]::IsInfinity($close) -or $close -le 0) { throw "Invalid close on $date" }
        [pscustomobject]@{date=$date.ToString('yyyy-MM-dd'); vix_close=$close.ToString('0.00########', $culture)}
    }
})
if (!$rows.Count) { throw 'Requested sample is empty.' }
$duplicates = @($rows | Group-Object date | Where-Object Count -gt 1)
if ($duplicates.Count) { throw 'Duplicate sample dates found; investigate before proceeding.' }
$originalDates = $rows.date -join ','
$rows = @($rows | Sort-Object date)
$wasSorted = ($originalDates -eq ($rows.date -join ','))
$weekends = @($rows | Where-Object { ([datetime]$_.date).DayOfWeek -in @('Saturday', 'Sunday') })
if ($weekends.Count) { throw 'Weekend observations found; investigate.' }
if ($rows[0].date -gt '2015-01-02' -or $rows[-1].date -lt '2025-12-31') { throw 'Sample does not cover expected endpoints.' }
$sourceSampleCount = $rows.Count
$calendarPath = Join-Path $root 'data/calendar/xnys_sessions_2015_2025.csv'
$calendarMetadata = Get-Content -LiteralPath (Join-Path $root 'data/calendar/metadata.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $calendarPath -Algorithm SHA256).Hash -ne $calendarMetadata.sha256) { throw 'Calendar snapshot hash mismatch.' }
$sessions = @(Import-Csv -LiteralPath $calendarPath)
$sessionDates = @{}
foreach ($session in $sessions) { $sessionDates[$session.date] = $true }
$observed = @{}
foreach ($row in $rows) { $observed[$row.date] = $true }
$missingSessions = @($sessions | Where-Object { !$observed.ContainsKey($_.date) })
if ($missingSessions.Count) { throw ('Missing expected trading sessions: ' + ($missingSessions.date -join ', ')) }
$excluded = @($rows | Where-Object { !$sessionDates.ContainsKey($_.date) } | ForEach-Object {
    [pscustomobject]@{date=$_.date; reason='Not an XNYS regular-session date; excluded from modelling only'}
})
$excluded | Export-Csv -LiteralPath (Join-Path $root 'data/excluded_dates.csv') -NoTypeInformation -Encoding UTF8
$rows = @($rows | Where-Object { $sessionDates.ContainsKey($_.date) })
if ($rows.Count -ne $sessions.Count) { throw 'Calendar reconciliation count mismatch.' }
$rows | Export-Csv -LiteralPath $processed -NoTypeInformation -Encoding UTF8
$absent = @(for ($day = [datetime]'2015-01-01'; $day -le [datetime]'2025-12-31'; $day = $day.AddDays(1)) {
    if ($day.DayOfWeek -notin @('Saturday','Sunday') -and !$observed.ContainsKey($day.ToString('yyyy-MM-dd'))) {
        [pscustomobject]@{date=$day.ToString('yyyy-MM-dd'); status='Absent in raw source; verified non-session under XNYS calendar'}
    }
})
$absent | Export-Csv -LiteralPath (Join-Path $root 'data/absent_weekdays.csv') -NoTypeInformation -Encoding UTF8
$counts = @($rows | Group-Object { $_.date.Substring(0,4) } | ForEach-Object { [pscustomobject]@{year=$_.Name; observations=$_.Count} })
$audit = [ordered]@{
    source_url=$url
    source_page='https://www.cboe.com/tradable-products/vix/vix-historical-data/'
    raw_file_last_write_utc=(Get-Item -LiteralPath $raw).LastWriteTimeUtc.ToString('o')
    raw_sha256=(Get-FileHash -LiteralPath $raw -Algorithm SHA256).Hash
    processed_sha256=(Get-FileHash -LiteralPath $processed -Algorithm SHA256).Hash
    source_rows=$source.Count
    source_sample_rows=$sourceSampleCount
    sample_rows=$rows.Count
    first_date=$rows[0].date
    last_date=$rows[-1].date
    duplicate_dates=$duplicates.Count
    invalid_or_missing_sample_closes=0
    weekend_observations=$weekends.Count
    source_sample_was_sorted=$wasSorted
    absent_weekdays=$absent.Count
    calendar_status='Reconciled to frozen XNYS calendar; all expected sessions present; early closes retained.'
    calendar=$calendarMetadata
    excluded_non_session_rows=$excluded.Count
    missing_expected_sessions=$missingSessions.Count
    transformations=@('Filter 2015-01-01 through 2025-12-31 inclusive','Keep XNYS regular-session dates including early closes','Select DATE and CLOSE','Rename date and vix_close','ISO dates; ascending order; preserve observed closing values')
    counts_by_year=$counts
}
$audit | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'data/data_audit.json') -Encoding UTF8
$audit | ConvertTo-Json -Depth 5
