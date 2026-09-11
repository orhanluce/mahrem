import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Session,tckn,iban,luhn} from '../extension/engine.mjs';
import {readFileSync} from 'node:fs';

test('checksums distinguish valid and invalid identifiers',()=>{
  assert.equal(tckn('10000000146'),true);assert.equal(tckn('10000000145'),false);
  assert.equal(iban('TR78-9999-9999-9999-9999-9999-99'),true);
  assert.equal(iban('TR00 9999 9999 9999 9999 9999 99'),false);
  assert.equal(luhn('4111 1111 1111 1111'),true);assert.equal(luhn('4111 1111 1111 1112'),false);
});
test('Turkish text masks and restores without newline loss',()=>{
  const input='Müşteri: Ayşe Deneme\nTelefon: +90 555 000 11 22\nTCKN: 10000000146\nMail: x@example.com x@example.com';
  const session=new Session(), result=session.mask(input);
  assert.equal(result.count,5);
  assert.ok(result.text.includes('Müşteri: [KISI-1]\nTelefon:'));
  assert.equal(result.text.match(/\[EPOSTA-1\]/g).length,2);
  assert.equal(session.restore(result.text).text,input);
});
test('manual phrases are literal, not regex; whole URL wins over email',()=>{
  const session=new Session();
  assert.equal(session.mask('A.Ş. https://example.com/?email=x@example.com&secret=abc',['A.Ş.']).text,'[OZEL-1] [URL-1]');
});
test('separate sessions, collisions, reset, unknown tokens',()=>{
  const a=new Session(),b=new Session();
  a.mask('a@example.com');
  assert.equal(b.restore('[EPOSTA-1]').unknown,1);
  assert.throws(()=>a.mask('[EPOSTA-1]'),/rumuz/);
  a.clear();assert.equal(a.restore('[EPOSTA-1]').unknown,1);
});
test('manifest has no site access or networking and no automatic submission',()=>{
  const manifest=JSON.parse(readFileSync(new URL('../extension/manifest.json',import.meta.url)));
  assert.equal(manifest.manifest_version,3);
  assert.deepEqual(manifest.permissions,['clipboardWrite']);
  assert.equal(manifest.host_permissions,undefined);
  assert.equal(manifest.content_scripts,undefined);
  assert.ok(manifest.content_security_policy.extension_pages.includes("connect-src 'none'"));
});
