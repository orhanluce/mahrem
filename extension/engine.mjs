// Pure local text engine. No storage, DOM, network or provider dependency.
const digits = value => value.replace(/\D/g, '');
const tokenPattern = /\[[A-Z0-9_-]+-\d+\]/g;
export function tckn(value) {
  const s = digits(value), n = [...s].map(Number);
  if (s.length !== 11 || s[0] === '0' || new Set(s).size === 1) return false;
  const odd = n[0]+n[2]+n[4]+n[6]+n[8], even = n[1]+n[3]+n[5]+n[7];
  return n[9] === ((odd*7-even)%10+10)%10 && n[10] === n.slice(0,10).reduce((a,b)=>a+b,0)%10;
}
export function iban(value) {
  const s = value.replace(/[\s-]/g, '').toUpperCase();
  if (!/^TR\d{24}$/.test(s)) return false;
  const rearranged = (s.slice(4)+s.slice(0,4)).replace(/[A-Z]/g, c=>String(c.charCodeAt(0)-55));
  let rem = 0;
  for (const c of rearranged) rem = (rem*10+Number(c))%97;
  return rem === 1;
}
export function luhn(value) {
  const s = digits(value);
  if (s.length < 13 || s.length > 19 || new Set(s).size === 1) return false;
  return [...s].reduce((sum,c,i)=>{
    let n = Number(c);
    if (i%2 === s.length%2) { n*=2; if(n>9) n-=9; }
    return sum+n;
  },0)%10 === 0;
}
const rules = [
  ['URL', /\bhttps?:\/\/[^\s<>()]+/gi, 120],
  ['EPOSTA', /(?<![\w.+-])[\w.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+/g, 100],
  ['TCKN', /(?<!\d)[1-9]\d{10}(?!\d)/g, 95, tckn],
  ['IBAN', /(?<![A-Z0-9])TR(?:[ -]?\d){24}(?![A-Z0-9])/gi, 90, iban],
  ['KART', /(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)/g, 85, luhn],
  ['TELEFON', /(?<!\d)(?:\+?90[\s().-]*)?(?:0[\s().-]*)?5\d{2}[\s().-]*\d{3}[\s.-]*\d{2}[\s.-]*\d{2}(?!\d)/g, 80],
  ['IP', /(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)/g, 70, v=>v.split('.').every(n=>Number(n)<=255)],
];
const rolePattern = /\b(?:davac[ıi]|daval[ıi]|m[üu]vekkil|vekil|hasta|m[üu][şs]teri|ad[ıi ]*soyad[ıi]?)[ \t]*[:\-][ \t]*([A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü]+(?:[ \t]+[A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü]+){1,3})/gi;

export class Session {
  constructor() { this.originals = new Map(); this.tokens = new Map(); this.counters = new Map(); }
  mask(text, terms = []) {
    if (text.length > 500000) throw new Error('Metin çok uzun; daha küçük parçalara ayırın.');
    if (!text.trim()) throw new Error('Önce bir metin girin.');
    if (/\[[A-Z0-9_-]+-\d+\]/.test(text)) throw new Error('Kaynakta mevcut rumuz var. Çakışmayı önlemek için kontrol edin.');
    const found = [];
    const add = (start,value,type,priority)=>found.push({start,end:start+value.length,value,type,priority});
    for (const [type,pattern,priority,validate] of rules) {
      for (const match of text.matchAll(pattern)) {
        if (!validate || validate(match[0])) add(match.index,match[0],type,priority);
      }
    }
    for (const match of text.matchAll(rolePattern)) {
      add(match.index+match[0].lastIndexOf(match[1]), match[1], 'KISI', 60);
    }
    if (terms.length > 200) throw new Error('En fazla 200 özel ifade ekleyin.');
    for (const term of terms) {
      if (!term.trim()) continue;
      const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      for (const match of text.matchAll(new RegExp(escaped,'gi'))) add(match.index,match[0],'OZEL',110);
    }
    const selected = [];
    for (const item of found.sort((a,b)=>b.priority-a.priority || (b.end-b.start)-(a.end-a.start) || a.start-b.start)) {
      if (!selected.some(s=>item.start<s.end && s.start<item.end)) selected.push(item);
    }
    let cursor=0, output=''; const counts={};
    for(const item of selected.sort((a,b)=>a.start-b.start)) {
      const key=JSON.stringify([item.type,item.value]);
      let token=this.tokens.get(key);
      if(!token) {
        const count=(this.counters.get(item.type)||0)+1;
        this.counters.set(item.type,count);
        token=`[${item.type}-${count}]`;
        this.tokens.set(key,token); this.originals.set(token,item.value);
      }
      output+=text.slice(cursor,item.start)+token;
      cursor=item.end; counts[item.type]=(counts[item.type]||0)+1;
    }
    return {text:output+text.slice(cursor), counts, count:selected.length};
  }
  restore(text) {
    let count=0, unknown=0;
    const restored=text.replace(tokenPattern, token=>{
      if(!this.originals.has(token)) { unknown++; return token; }
      count++; return this.originals.get(token);
    });
    return {text:restored,count,unknown};
  }
  clear() { this.tokens.clear(); this.originals.clear(); this.counters.clear(); }
}
