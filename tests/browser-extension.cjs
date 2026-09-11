// Optional real-browser test: npm install --no-save playwright; node tests/browser-extension.cjs
const {chromium}=require('playwright');
const {mkdtempSync,readFileSync,mkdirSync}=require('node:fs');
const {tmpdir}=require('node:os');
const path=require('node:path');
const assert=require('node:assert/strict');
(async()=>{
  const root=path.resolve(__dirname,'..');
  const profile=mkdtempSync(path.join(tmpdir(),'mahrem-extension-'));
  const extension=path.join(root,'extension');
  const context=await chromium.launchPersistentContext(profile,{
    channel:'chromium',headless:true,acceptDownloads:true,
    args:[`--disable-extensions-except=${extension}`,`--load-extension=${extension}`],
  });
  try {
    let worker=context.serviceWorkers()[0];
    if(!worker) worker=await context.waitForEvent('serviceworker');
    const id=new URL(worker.url()).host;
    const page=await context.newPage();
    const external=[];
    page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    await page.goto(`chrome-extension://${id}/workspace.html`);
    await page.locator('#source').fill('Müşteri: Ayşe Deneme\nE-posta: private@example.com');
    await page.locator('#mask').click();
    assert.equal(await page.locator('#masked').inputValue(),'Müşteri: [KISI-1]\nE-posta: [EPOSTA-1]');
    assert.equal(await page.locator('#copy').isDisabled(),true);
    await page.locator('#review').check();
    await page.locator('#copy').click();
    await page.waitForFunction(()=>document.getElementById('status').textContent.includes('panoya'));
    await page.locator('#reply').fill('Yanıt: [EPOSTA-1]');
    const downloading=page.waitForEvent('download');
    await page.locator('#restore').click();
    const download=await downloading;
    assert.equal(readFileSync(await download.path(),'utf8'),'Yanıt: private@example.com');
    await page.locator('#source').fill('changed@example.com');
    assert.equal(await page.locator('#copy').isDisabled(),true);
    assert.equal(await page.locator('#masked').inputValue(),'');
    await page.locator('#mask').click();
    mkdirSync(path.join(root,'tmp'),{recursive:true});
    await page.screenshot({path:path.join(root,'tmp/extension-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:path.join(root,'tmp/extension-mobile.png'),fullPage:true});
    page.on('dialog',dialog=>dialog.accept());
    await page.locator('#clear').click();
    assert.equal(await page.locator('#source').inputValue(),'');
    assert.equal(await page.locator('#restore').isDisabled(),true);
    assert.deepEqual(external,[]);
    console.log('Extension loaded: mask, review, clipboard, restore download, stale-input reset, responsive layout, clear, zero HTTP requests passed.');
  } finally {await context.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
