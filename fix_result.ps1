$file = 'src\lib\components\fallacy\FallacyResult.svelte'
$content = Get-Content $file -Raw -Encoding UTF8

# 1. Remove BarChart2 import line
$content = $content -replace "`t`tBarChart2,`r`n", ''

# 2. Add base import after lucide import closing brace line
$content = $content -replace "(`t} from 'lucide-svelte';)", "`$1`r`n`timport { base } from '`$app/paths';"

# 3. Fix empty catch block: } catch (_) {}
$old3 = "} catch (_) {}"
$new3 = "} catch {`r`n`t`t`t// user cancelled share or share failed`r`n`t`t}"
$content = $content.Replace($old3, $new3)

# 4. Add keys to chartData each blocks (there are 2)
$content = $content -replace '\{#each chartData as item, i\}', '{#each chartData as item, i (item.label)}'

# 5. Add key to fallacies_found each block
$old5 = '{#each analysis.fallacies_found as fallacy, idx}'
$new5 = '{#each analysis.fallacies_found as fallacy, idx (fallacy.type + "-" + idx)}'
$content = $content.Replace($old5, $new5)

# 6. Fix href="/fallacy" -> href="{base}/fallacy"
$content = $content.Replace('href="/fallacy"', 'href="{base}/fallacy"')

[System.IO.File]::WriteAllText((Resolve-Path $file).Path, $content, [System.Text.Encoding]::UTF8)
Write-Host "All fixes applied."
