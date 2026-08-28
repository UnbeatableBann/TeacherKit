Get-ChildItem -Path src -Filter *.tsx -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'text-indigo-600', 'text-[var(--color-primary)]'
    $content = $content -replace 'bg-indigo-600', 'bg-[var(--color-primary)]'
    $content = $content -replace 'hover:bg-indigo-700', 'hover:bg-[var(--color-primary-hover)]'
    $content = $content -replace 'ring-indigo-500', 'ring-[var(--color-primary)]'
    $content = $content -replace 'bg-indigo-50/50', 'bg-[var(--color-primary)]/10'
    $content = $content -replace 'border-l-indigo-600', 'border-l-[var(--color-primary)]'
    Set-Content -Path $_.FullName -Value $content -Encoding UTF8
}
