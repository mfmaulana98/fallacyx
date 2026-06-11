$f = Get-Content 'src\lib\components\fallacy\FallacyResult.svelte' -Raw -Encoding UTF8

if ($f -match 'BarChart2') { Write-Host 'FAIL: BarChart2 still present' } else { Write-Host 'OK: BarChart2 removed' }
if ($f -match "base.*app/paths") { Write-Host 'OK: base imported' } else { Write-Host 'FAIL: base import missing' }
if ($f -match 'catch \(_\) \{\}') { Write-Host 'FAIL: old catch still present' } else { Write-Host 'OK: catch fixed' }
$keys = ([regex]::Matches($f, '#each chartData as item, i \(')).Count
Write-Host ('chartData each keys found: ' + $keys + '/2')
if ($f -match 'fallacies_found as fallacy, idx \(') { Write-Host 'OK: fallacies_found key present' } else { Write-Host 'FAIL: fallacies_found key missing' }
if ($f -match 'href="\{base\}/fallacy"') { Write-Host 'OK: href uses base' } else { Write-Host 'FAIL: href not fixed' }
