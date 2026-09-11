param(
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA 'Mahrem'),
    [switch]$NoOpen
)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$sourceRoot = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path (Join-Path $sourceRoot 'pyproject.toml'))) {
    throw 'ZIP dosyasini once tamamen bir klasore cikarin; sonra Kur.bat dosyasini acin.'
}
Write-Host 'Mahrem kuruluyor. Ilk kurulumda internet gerekir; belgeleriniz okunmaz.'
New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
$InstallRoot = (Resolve-Path -LiteralPath $InstallRoot).Path
$uvCommand = Get-Command uv -ErrorAction SilentlyContinue
if ($uvCommand) {
    $uvExe = $uvCommand.Source
} else {
    Write-Host 'Gerekli kurulum araci resmi Astral kaynagindan indiriliyor...'
    $bootstrap = Join-Path $InstallRoot 'uv-install.ps1'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://astral.sh/uv/0.11.21/install.ps1' -OutFile $bootstrap
    $env:UV_INSTALL_DIR = Join-Path $InstallRoot 'tools'
    $env:UV_NO_MODIFY_PATH = '1'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $bootstrap
    if ($LASTEXITCODE -ne 0) { throw 'Kurulum araci indirilemedi.' }
    $uvExe = Join-Path $env:UV_INSTALL_DIR 'uv.exe'
}
$runtime = Join-Path $InstallRoot 'runtime'
$python = Join-Path $runtime 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    Write-Host 'Python hazirlaniyor...'
    & $uvExe venv --python 3.11 $runtime
    if ($LASTEXITCODE -ne 0) { throw 'Python hazirlanamadi.' }
}
Write-Host 'Mahrem ve bagimliliklari kuruluyor...'
& $uvExe pip install --python $python $sourceRoot
if ($LASTEXITCODE -ne 0) { throw 'Mahrem kurulumu basarisiz oldu.' }
& $python -c 'from mahrem.server import mcp; assert mcp is not None'
if ($LASTEXITCODE -ne 0) { throw 'Kurulum kontrolu basarisiz oldu.' }
$command = Join-Path $runtime 'Scripts\mahrem-mcp.exe'
$config = @{ mcpServers = @{ mahrem = @{ command = $command; args = @(); env = @{ PYTHONUTF8 = '1' } } } }
$configPath = Join-Path $InstallRoot 'claude-baglanti.json'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($configPath, ($config | ConvertTo-Json -Depth 8), $utf8)
$notePath = Join-Path $InstallRoot 'BAGLANTI.txt'
$note = @"
MAHREM KURULDU

Codex / yerel MCP destekli masaustu uygulamasi:
Ayarlar > MCP sunuculari > Sunucu ekle > STDIO
Ad: mahrem
Komut: $command
Argumanlar: bos birakin
Kaydedin ve uygulamayi yeniden baslatin.

Claude Desktop:
Indirdiginiz klasorde Claude-Bagla.bat dosyasina cift tiklayin.
Claude > Ayarlar > Developer > Edit Config ile ayar dosyasinin yerini bulun.
Baglanti yardimcisinda bu dosyayi secin. Mevcut ayarlar yedeklenir.
Elle baglanti icin hazir ayarlar: $configPath
Claude'u tamamen kapatip yeniden acin.

Rehber: https://github.com/orhanluce/mahrem/blob/main/docs/KOLAY-KURULUM.md

Ilk denemede gercek musteri belgesi kullanmayin.
Sohbete belge yuklemeyin; yalnizca dosyanin yolunu verin.
Bu surum yalnizca TXT ve Markdown destekler. Tum isimleri otomatik bulamaz.
"@
[IO.File]::WriteAllText($notePath, $note, $utf8)
Write-Host "Kurulum dogrulandi. Baglanti rehberi: $notePath"
if (-not $NoOpen) { Start-Process notepad.exe -ArgumentList ('"' + $notePath + '"') }
