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
- 0.2; UTF-8 TXT/MD, DOCX ve metin PDF okur, yalnızca düz metin çıktısı verir. Orijinal Word/PDF üzerinde kalıcı karartma yapmaz. Görsel, ek ve form metni eksik kalabilir. OCR, eski DOC ve şifreli PDF desteklenmez.
- Tarayıcı eklentisi ayrı bir yerel sekmedir; site içeriğine erişmez ve gönderim/yükleme engellemez. Ağ bağlantısı CSP ile kapatılmıştır. Ham metni önce sohbet sitesine yapıştırmayın.
- Tarayıcı ve MCP eşleştirme tabloları ayrıdır. Sekmeyi yenilemek/kapatmak tarayıcı tablosunu siler. Temizleme, panodaki veya indirilmiş dosyalardaki verileri silmez.
- Otomatik tespit hatasiz degildir. Hukuk, saglik veya finans belgelerinde rumuzlu dosyayi kullanmadan once yerel olarak kontrol edin.

Guvenlik acigi bildirirken ornek dosyaya gercek kisisel veri koymayin.
