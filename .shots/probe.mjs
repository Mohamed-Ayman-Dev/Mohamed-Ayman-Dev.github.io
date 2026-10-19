// Ad-hoc CDP driver used to verify the restyle (screenshots, overflow, console).
import { writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const PORT = process.env.PORT || 9222;
const BASE = process.env.BASE || 'http://localhost:8765/?v=9';
const OUT = new URL('.', import.meta.url).pathname;

const targets = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const page = targets.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));

let id = 0;
const pending = new Map();
const logs = [];
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') logs.push('EXCEPTION: ' + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type))
    logs.push(m.params.type.toUpperCase() + ': ' + m.params.args.map(a => a.value ?? a.description).join(' '));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error')
    logs.push('LOG: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
});
const send = (method, params = {}) => new Promise(res => {
  const n = ++id;
  pending.set(n, m => res(m.result ?? m.error));
  ws.send(JSON.stringify({ id: n, method, params }));
});
const evaluate = async expr => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result?.value;
const shoot = async name => {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(OUT + name, Buffer.from(r.data, 'base64'));
};

await send('Page.enable');
await send('Runtime.enable');
await send('Log.enable');

async function run(label, metrics, sections) {
  await send('Emulation.setDeviceMetricsOverride', metrics);
  await send('Page.navigate', { url: BASE + '&' + label });
  await sleep(3500);
  const overflow = await evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth');
  const bodyOverflow = await evaluate('document.body.scrollWidth - document.body.clientWidth');
  console.log(`[${label}] horizontal overflow: html=${overflow} body=${bodyOverflow}`);
  for (const s of sections) {
    await evaluate(`(${s.js})`);
    await sleep(s.wait ?? 1400);
    await shoot(`${label}-${s.name}.png`);
  }
}

const scrollTo = sel => `document.querySelector('${sel}').scrollIntoView({block:'start'})`;

await run('desktop', { width: 1440, height: 900, deviceScaleFactor: 2, mobile: false }, [
  { name: 'hero', js: 'scrollTo(0,0)' },
  { name: 'about', js: scrollTo('#about') },
  { name: 'experience', js: scrollTo('#experience') },
  { name: 'skills', js: scrollTo('#skills') },
  { name: 'projects', js: scrollTo('#projects'), wait: 2200 },
  { name: 'projects2', js: `document.querySelectorAll('.proj-card')[1].scrollIntoView({block:'center'})`, wait: 2200 },
  { name: 'contact', js: scrollTo('#contact') },
  { name: 'lightbox', js: `document.querySelector('.proj-card .shot-strip img').click()`, wait: 1200 },
]);

await run('mobile', { width: 390, height: 844, deviceScaleFactor: 3, mobile: true }, [
  { name: 'hero', js: 'scrollTo(0,0)' },
  { name: 'menu', js: `document.getElementById('navToggle').click()`, wait: 700 },
  { name: 'about', js: `document.getElementById('navToggle').click(); ${scrollTo('#about')}` },
  { name: 'experience', js: scrollTo('#experience') },
  { name: 'skills', js: scrollTo('#skills') },
  { name: 'projects', js: scrollTo('#projects'), wait: 2200 },
  { name: 'contact', js: scrollTo('#contact') },
]);

console.log('console issues:', logs.length ? logs : 'none');
ws.close();
