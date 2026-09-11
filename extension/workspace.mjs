import {Session} from './engine.mjs';
const session=new Session();
const el=id=>document.getElementById(id);
let ready=false;
function invalidate() {
  ready=false; el('review').checked=false; el('copy').disabled=true;
  el('masked').value=''; el('counts').textContent='Metin değişti; yeniden maskeleyin.';
}
el('source').addEventListener('input',invalidate);
el('terms').addEventListener('input',invalidate);
el('mask').addEventListener('click',()=>{
  invalidate();
  try {
    const result=session.mask(el('source').value,el('terms').value.split(/\r?\n/).map(s=>s.trim()).filter(Boolean));
    el('masked').value=result.text;
    el('counts').textContent=`${result.count} alan maskelendi. `+Object.entries(result.counts).map(([k,v])=>`${k}: ${v}`).join(' · ');
    el('status').textContent='Kopyalamadan önce maskeli metni kontrol edin.';
    ready=true; el('restore').disabled=false;
  } catch(error) { el('status').textContent=error.message; }
});
el('review').addEventListener('change',()=>{el('copy').disabled=!(ready&&el('review').checked);});
el('copy').addEventListener('click',async()=>{
  if(!ready||!el('review').checked) return;
  try { await navigator.clipboard.writeText(el('masked').value); el('status').textContent='Yalnızca maskeli kopya panoya alındı. Sohbete yapıştırabilirsiniz.'; }
  catch { el('status').textContent='Pano erişilemedi; maskeli metni seçip kendiniz kopyalayın.'; }
});
el('restore').addEventListener('click',()=>{
  const reply=el('reply').value;
  if(!reply.trim()) {el('status').textContent='Önce yanıtı yapıştırın.';return;}
  const result=session.restore(reply);
  if(result.unknown) {el('status').textContent=`${result.unknown} bilinmeyen rumuz var. Yanıtı ve oturumu kontrol edin; dosya indirilmedi.`;return;}
  const url=URL.createObjectURL(new Blob([result.text],{type:'text/plain;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download='mahrem-sonuc.txt';link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  el('status').textContent=`${result.count} rumuz geri açıldı; indirme başlatıldı.`;
});
el('clear').addEventListener('click',()=>{
  if(!confirm('Bu sekmedeki metin ve geri açma tablosu silinsin mi?')) return;
  session.clear(); for(const id of ['source','terms','masked','reply']) el(id).value='';
  invalidate(); el('restore').disabled=true;
  el('status').textContent='Oturum temizlendi. Sistem panosu ve indirilmiş dosyalar silinmedi.';
});
