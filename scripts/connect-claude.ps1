param(
    [string]$ConfigPath,
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'Mahrem')
)
$ErrorActionPreference = 'Stop'
$ready = Join-Path $InstallRoot 'claude-baglanti.json'
if (-not (Test-Path -LiteralPath $ready)) { throw 'Once Kur.bat dosyasini calistirin.' }
if (-not $ConfigPath) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        'Claude > Ayarlar > Developer > Edit Config ile ayar dosyasinin yerini bulun. Sonraki pencerede bu dosyayi secin. Mevcut ayarlar yedeklenecek ve yalnizca Mahrem eklenecek.',
        'Claude baglantisi'
    ) | Out-Null
    $picker = New-Object System.Windows.Forms.OpenFileDialog
    $picker.Filter = 'Claude ayar dosyasi (claude_desktop_config.json)|claude_desktop_config.json'
    $picker.InitialDirectory = Join-Path $env:APPDATA 'Claude'
    if ($picker.ShowDialog() -ne 'OK') { Write-Host 'Baglanti iptal edildi.'; exit 0 }
    $ConfigPath = $picker.FileName
}
$content = [IO.File]::ReadAllText($ConfigPath)
if ([string]::IsNullOrWhiteSpace($content)) { $content = '{}' }
$config = $content | ConvertFrom-Json
if ($config -isnot [pscustomobject]) { throw 'Ayar dosyasi bir JSON nesnesi olmali; dosya degistirilmedi.' }
if (-not $config.PSObject.Properties['mcpServers']) {
    $config | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{})
}
if ($config.mcpServers -isnot [pscustomobject]) { throw 'mcpServers alani gecersiz; dosya degistirilmedi.' }
$newEntry = (Get-Content -Raw -LiteralPath $ready | ConvertFrom-Json).mcpServers.mahrem
if ($config.mcpServers.PSObject.Properties['mahrem']) {
    if ($config.mcpServers.mahrem.command -eq $newEntry.command) {
        Write-Host 'Mahrem zaten bagli. Claude uygulamasini yeniden baslatin.'
        exit 0
    }
    throw 'mahrem adinda farkli bir baglanti var; mevcut ayar korunarak islem durduruldu.'
}
$backup = $ConfigPath + '.mahrem-backup-' + [guid]::NewGuid().ToString('N')
Copy-Item -LiteralPath $ConfigPath -Destination $backup
$config.mcpServers | Add-Member -NotePropertyName mahrem -NotePropertyValue $newEntry
$json = $config | ConvertTo-Json -Depth 100
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($ConfigPath, $json, $utf8)
Write-Host 'Mahrem eklendi. Claude uygulamasini tamamen kapatip yeniden acin.'
Write-Host "Onceki ayarlarin yedegi: $backup"
