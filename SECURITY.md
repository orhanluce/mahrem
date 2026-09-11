# Güvenlik modeli

Mahrem'in amacı, ham hassas içeriğin model sağlayıcısına gönderilmesini önlemektir. Bunun için MCP araçları metin değil, **mutlak yerel dosya yolu** kabul eder.

## Guvenli sinir

- `scan_file` ve `mask_file` kaynak dosyayi yerel surecte okur.
- Modele yalnizca rumuzlu metin, sayimlar ve dosya yollari doner.
- `restore_file` acik metni yerel dosyaya yazar; acik metni arac yanitinda dondurmez.
- Rumuz-eslesme tablosu yalnizca calisan MCP surecinin belleğinde tutulur.
- Mahrem'in kendi kodunda ağ çağrısı, telemetri ve API anahtarı yoktur.

## Sinirlamalar

- Hassas metin sohbete yapistirildiysa koruma icin gec kalinmistir.
- MCP sureci kapaninca geri acma tablosu kaybolur. Kalici sifreli kasa henuz yoktur.
- V0 yalnizca UTF-8 `.txt` ve `.md` dosyalarini destekler.
- Otomatik tespit hatasiz degildir. Hukuk, saglik veya finans belgelerinde rumuzlu dosyayi kullanmadan once yerel olarak kontrol edin.

Guvenlik acigi bildirirken ornek dosyaya gercek kisisel veri koymayin.
