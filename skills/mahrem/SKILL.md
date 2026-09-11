---
name: mahrem
description: Yerel TXT veya Markdown dosyalarini Claude, ChatGPT ya da Codex ile islemeden once hassas verileri rumuzlamak ve is bittikten sonra cihazda geri acmak icin kullan. Kullanici gizlilik, anonimlestirme, maskeleme, TCKN, IBAN, telefon, e-posta veya hassas belge dediginde tetikle. Sohbete zaten yapistirilmis ham metni korudugunu iddia etme.
---

# Mahrem dosya akisi

Bu skill bir talimat katmanidir. Gercek maskeleme `mahrem` yerel MCP araclariyla yapilir.

## Degismez guvenlik kurallari

- Kullanicidan hassas metni sohbete yapistirmasini isteme.
- Ham belge icerigini arac argumani olarak gonderme. Yalnizca mutlak yerel dosya yolu kullan.
- Geri acilan dosyayi okuma, ozetleme veya sohbette gosterme. Yalnizca yolunu kullaniciya bildir.
- Bir metin daha once sohbete yapistirildiysa bunun geri alinamayacagini acikca belirt.
- Oturum kapanmadan once geri acma islemini tamamla; eslesme tablosu diske yazilmaz.

## Is akisi

1. Kullanicidan yerel `.txt` veya `.md` dosyasinin mutlak yolunu iste ya da verdigi yolu kullan.
2. Istenirse `scan_file` ile yalnizca tur ve adet raporu cikar.
3. `mask_file` cagrisini yap. Bundan sonra yalnizca `masked_text` ile calis.
4. Urettigin sonucu, `[TCKN-1]`, `[KISI-1]` gibi yer tutuculari aynen koruyarak yeni bir maskeli dosyaya yaz.
5. Kullanicinin son dosyayi istemesi halinde `restore_file` ile yerel acik metin dosyasini olustur.
6. Geri acilan dosyayi yeniden okuma. Yolunu bildir ve `forget_session` ile bellek ici eslesmeyi sil.

## Kapsam siniri

V0; TCKN, TR IBAN, Turkiye cep telefonu, e-posta, Luhn uyumlu kart numarasi, IPv4, URL ve belirli rol etiketlerinden sonra gelen kisi adlarini tespit eder. Isim ve kurum tespiti eksik kalabilir. Kullanici `rules.json` icinde yerel literal kurallar ekleyebilir; bu dosyanin icerigini de sohbete tasima.
