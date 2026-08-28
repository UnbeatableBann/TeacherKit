Get-ChildItem -Path src -Filter *.tsx -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'indigo-50', '[var(--color-primary)]/10'
    $content = $content -replace 'indigo-100', '[var(--color-primary)]/20'
    $content = $content -replace 'indigo-300', '[var(--color-primary)]/40'
    $content = $content -replace 'indigo-500', '[var(--color-primary)]'
    $content = $content -replace 'indigo-700', '[var(--color-primary-hover)]'
    Set-Content -Path $_.FullName -Value $content -Encoding UTF8
}
