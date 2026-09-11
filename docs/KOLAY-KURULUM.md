# Mahrem'i kurun ve ilk belgenizi deneyin

Bu rehber için kod bilmeniz veya komut yazmanız gerekmiyor. Windows 10/11 bilgisayarınız ve internet bağlantınız yeterli. Kurulum gerekli Python ortamını kendisi hazırlar. Mahrem ücretsizdir; kullandığınız yapay zekâ uygulamasının kendi ücretleri ayrı olabilir.

**[Windows için indir](https://github.com/orhanluce/mahrem/archive/refs/heads/main.zip)**

## 1. İndirin ve kurun

1. Yukarıdaki bağlantıyla ZIP dosyasını indirin.
2. ZIP'e sağ tıklayın, **Tümünü ayıkla** seçeneğini seçin.
3. Açılan `mahrem-main` klasöründe **Kur.bat** dosyasına çift tıklayın.
4. Kurulum penceresi açık kalsın. Bittiğinde bağlantı bilgilerinizi içeren bir Not Defteri penceresi açılır.

Git veya Python'ı önceden kurmanız gerekmez. İlk kurulum internetten Python ve yazılım paketlerini indirir. Belge içerikleri kurulum sırasında okunmaz. Kurucu yönetici yetkisi istemez; dosyaları kullanıcı hesabınızın `AppData\Local\Mahrem` klasörüne yerleştirir.

Kurulum dosyası henüz dijital olarak imzalanmış değildir. Windows veya kurumunuz çalıştırmayı engellerse korumaları kapatmayın; kurumunuzun bilişim birimine bu depo bağlantısını iletin.

## 2. Kullandığınız uygulamaya bağlayın

### Codex masaüstü

1. **Ayarlar → MCP sunucuları → Sunucu ekle** bölümünü açın.
2. Bağlantı türünü **STDIO** seçin.
3. Ad alanına **mahrem** yazın. Komut alanına kurulum sonunda açılan dosyadaki **Komut:** satırının karşısındaki yolu kopyalayın. Argümanları boş bırakın.
4. Kaydedin ve uygulamayı yeniden başlatın.

Menü adları uygulama sürümüne göre değişebilir. Yerel STDIO seçeneği bulunmayan bir uygulama bu kurulum yolunu kullanamaz.

### Claude masaüstü (Claude Desktop)

1. **Ayarlar → Geliştirici (Developer) → Yapılandırmayı düzenle (Edit Config)** yolunu izleyin.
2. İndirdiğiniz Mahrem klasöründe **Claude-Bagla.bat** dosyasına çift tıklayın.
3. Açılan dosya seçme penceresinde Claude'un `claude_desktop_config.json` dosyasını seçin.
4. Yardımcı mevcut ayarlarınızı yedekler ve diğer bağlantıları koruyarak Mahrem'i ekler. Kod veya JSON düzenlemeniz gerekmez.
5. Claude'u tamamen kapatıp yeniden açın. Araçlar arasında Mahrem'in göründüğünü kontrol edin.

`Kur.bat` yalnızca kurulumu yapar; seçtiğiniz Claude ayar dosyasını `Claude-Bagla.bat` günceller. Bu bağlantı adımı uygulamanın kendi yerel araç desteğini kullanır; tarayıcıdan açılan Claude sohbetiyle aynı değildir.

### ChatGPT veya Claude'u tarayıcıda kullanıyorsanız

Bu sürüm tarayıcıya tek tıkla eklenen bir uzantı değildir. Web sohbetine yüklediğiniz ham belgeyi önceden maskeleyemez. Yerel araç destekleyen masaüstü uygulamasını kullanın. Web için gönderimden önce çalışan tarayıcı eklentisi henüz hazırlanmadı.

## 3. Önce örnek belgeyle deneyin

İndirdiğiniz klasörde `examples/ornek-belge.txt` dosyası bulunur. Bu dosyaya **Shift + sağ tık → Yol olarak kopyala** yapın. Sohbete yalnızca bu yolu vererek şunu yazın:

> Mahrem aracını kullanarak şu yerel dosyayı maskele: DOSYA_YOLU. Kaynak dosyayı başka bir araçla okuma. Şimdilik sadece hangi veri türlerinden kaç tane maskelendiğini söyle.

`DOSYA_YOLU` yerine kopyaladığınız yolu yapıştırın. Ajanın Mahrem aracını kullandığını kontrol edin. Örnek dosyada e-posta, IBAN, IP, kişi, TCKN ve telefon için birer tespit beklenir.

Maskeleme sonunda aynı klasörde `.masked.txt` ile biten bir kopya oluşur. Bu kopyayı kendiniz Not Defteri'nde açın ve kontrol edin. Belgenizde açıkta kalan isim veya başka bilgiler varsa AI ile işlemeye devam etmeyin; bu ilk sürüm tüm kişisel verileri bulmaz.

## 4. Belgenizle çalışın

Şimdilik `.txt` ve `.md` dosyaları desteklenir. Word belgesinin bir kopyasını **Düz Metin (.txt), UTF-8** olarak kaydedin; biçimlendirme kaybolabilir. PDF dosyasını doğrudan vermeyin.

Kontrol ettiğiniz maskeli metin için örnek istek:

> Yalnızca Mahrem'in maskeli çıktısıyla çalış. Metni daha anlaşılır biçimde düzenle. Köşeli parantezli rumuzları aynen koru. Sonucu yeni bir maskeli dosyaya kaydet.

Gerçek bilgileri sonuç dosyasına geri koymak için:

> Aynı Mahrem oturumunu kullanarak sonuç dosyasını yerelde geri aç. Geri açılan dosyayı okuma ve içeriğini sohbette gösterme; yalnızca dosya yolunu bildir.

İşlemi tamamlayana kadar uygulamayı kapatmayın: geri açma tablosu yalnızca bellekte tutulur. Uygulama veya Mahrem sunucusu yeniden başlarsa o tablonun geri getirilmesi mümkün değildir; kaynak belgeniz korunur.

## Bir şey çalışmadıysa

| Durum | Yapılacak işlem |
|---|---|
| Kur.bat bulunamıyor | ZIP'i tamamen ayıklayın, `mahrem-main` klasörünü açın. |
| Kurulum indirme hatası verdi | İnternet bağlantısını kontrol edin. Kurumsal ağ engelinde bilişim birimine başvurun. |
| Mahrem araçlarda görünmüyor | Komut yolunu kurulumun oluşturduğu dosyadan kopyalayın; uygulamayı tamamen yeniden başlatın. |
| Dosya bulunamadı | Dosyayı bilgisayarınıza kaydedin; “Yol olarak kopyala” ile tam yolunu verin. |
| Oturum bulunamadı | Sunucu yeniden başlamış olabilir. Kaynak belgeyi yeniden maskeleyerek yeni bir işlem başlatın. |

Sorun bildirirken [GitHub Issues](https://github.com/orhanluce/mahrem/issues) kullanabilirsiniz. Müvekkil belgesi veya kişisel veri paylaşmadan yalnızca hata mesajını yazın.

Teknik referanslar: [uv kurulumu](https://docs.astral.sh/uv/getting-started/installation/), [yerel MCP bağlantısı](https://modelcontextprotocol.io/docs/develop/connect-local-servers), [Codex MCP ayarları](https://learn.chatgpt.com/docs/extend/mcp).
