# Mahrem tarayıcı eklentisi

ChatGPT veya Claude'u tarayıcıdan kullanıyorsanız bu yolu seçin. Python, sunucu, API anahtarı veya Mahrem hesabı gerekmez. Eklenti ücretsiz ve açık kaynaktır; yapay zekâ hizmetinin kendi ücretleri ayrı olabilir.

## 1. İndirin ve ekleyin

1. **[Mahrem'i indirin](https://github.com/orhanluce/mahrem/archive/refs/heads/main.zip)**. ZIP dosyasını **Tümünü ayıkla** ile kalıcı bir klasöre açın.
2. Chrome adres çubuğuna `chrome://extensions`, Edge kullanıyorsanız `edge://extensions` yazın.
3. **Geliştirici modu** anahtarını açın.
4. **Paketlenmemiş öğe yükle / Load unpacked** düğmesine basın.
5. İndirdiğiniz `mahrem-main` klasörünün **içindeki `extension` klasörünü** seçin. Ana klasörü veya ZIP'i seçmeyin.
6. Tarayıcının uzantılar menüsünden Mahrem'i sabitleyin. Mahrem simgesine tıklayın; ayrı bir çalışma sekmesi açılır.

Henüz Chrome/Edge mağazasında değil; bu yüzden mağazadan tek tıkla kurulum yok. Kurumunuz geliştirici modunu engelliyorsa güvenlik ayarlarını aşmayın, bilişim biriminize danışın. Klasörü daha sonra taşımayın veya silmeyin.

## 2. Önce Mahrem'de maskeleyin

1. Hassas metni **sohbet sitesine değil, Mahrem sekmesindeki ilk kutuya** yapıştırın.
2. Özellikle gizlemek istediğiniz kişi, kurum veya adresleri ek terimler kutusuna, her satıra bir ifade olacak şekilde yazın. Bunlar birebir eşleşir; farklı yazılışları ayrıca ekleyin.
3. **Maskele** düğmesine basın.
4. Maskeli metni okuyun. Açıkta kalan bilgi varsa ek terimlere yazıp yeniden maskeleyin. Otomatik tespit bütün isimleri ve kişisel bilgileri bulmaz.
5. Kontrol onayını işaretleyin; kopyalama düğmesi açılır. Çıktıyı kopyalayıp ChatGPT veya Claude'a yapıştırın.

Örnek istek: “Bu metni düzenle. `[KISI-1]` gibi köşeli parantezli rumuzları değiştirme.”

Eklenti sohbet sitelerini okumaz. Gönder tuşunu engellemez, yüklediğiniz belgeleri otomatik maskelemez. Ham metni önce sohbete yapıştırdıysanız Mahrem bunu geri alamaz.

## 3. Yanıtta gerçek bilgileri geri koyun

1. Yapay zekânın rumuzlu yanıtını kopyalayın.
2. **Aynı Mahrem sekmesindeki** yanıt kutusuna yapıştırın.
3. Geri açma/indirme düğmesiyle TXT dosyasını bilgisayarınıza indirin. Açık metni yeniden sohbete göndermeyin.

Bilinmeyen rumuz varsa indirme durur. Yanıtın rumuzları değiştirmediğini ve doğru Mahrem sekmesinde olduğunuzu kontrol edin.

İşiniz bitene kadar sekmeyi kapatmayın veya yenilemeyin: geri açma tablosu yalnızca bellektedir. Masaüstü Mahrem oturumuyla paylaşılmaz. Temizleme işlemi panonuzu veya önceden indirilmiş dosyaları silmez.

## Word ve PDF kullanacaksanız

Tarayıcı eklentisi şu an **yapıştırılan metni** işler; Word/PDF dosyası yükleme alanı yoktur. Belgeden metin kopyalayabilir veya [masaüstü kurulumuyla](KOLAY-KURULUM.md) DOCX/metin PDF dosyanızın maskeli TXT kopyasını oluşturabilirsiniz. Biçim koruma ve taranmış belge için OCR desteği yoktur.

## Güncelleme ve sorun çözme

Önce açık işi tamamlayın. Yeni ZIP'i ayıklayın; eski Mahrem eklentisini kaldırıp yeni `extension` klasörünü aynı adımlarla yükleyin. Kurulumda “manifest bulunamadı” hatası alırsanız seçtiğiniz klasörün doğrudan `manifest.json` içerdiğini kontrol edin.

Kaynak: [Chrome'un resmi yerel eklenti yükleme rehberi](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world).
