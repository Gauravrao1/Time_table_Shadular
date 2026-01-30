(function(){
  const apiUrlInput = document.getElementById('apiUrl');
  const daysPresetSelect = document.getElementById('daysPreset');
  const uploadForm = document.getElementById('uploadForm');
  const generateBtn = document.getElementById('generateBtn');
  const testBtn = document.getElementById('testBtn');
  const seedBtn = document.getElementById('seedBtn');
  const quickRunBtn = document.getElementById('quickRunBtn');
  const timetableRoot = document.getElementById('timetable');

  const DEFAULT_SLOTS = ['09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00'];
  let currentApiBase = null;

  // Warn if opened from file://
  if(location.protocol === 'file:'){
    notify('Open via http:// (run: python -m http.server 5173 in frontend/)', true);
  }

  // Initial health check (non-blocking)
  health().then(base => { currentApiBase = base; }).catch(() => notify('Backend not reachable at ' + getApiBase(), true));

  apiUrlInput?.addEventListener('change', () => {
    currentApiBase = null;
    health().then((base) => { currentApiBase = base; notify('Connected to: ' + base); }).catch(() => notify('Backend not reachable at ' + getApiBase(), true));
  });

  testBtn?.addEventListener('click', async () => {
    try{
      setLoading(true);
      currentApiBase = null;
      const base = await health();
      currentApiBase = base;
      notify('Connected to: ' + base);
    }catch(err){
      notify('Test failed: ' + (err.message || String(err)), true);
    }finally{
      setLoading(false);
    }
  });

  seedBtn?.addEventListener('click', async () => {
    try{
      setLoading(true);
      const res = await fetch(api('/api/seed'), { method: 'POST' });
      await ensureOk(res);
      notify('Sample data loaded');
    }catch(err){
      notify('Seed failed: ' + (err.message || String(err)), true);
    }finally{
      setLoading(false);
    }
  });

  quickRunBtn?.addEventListener('click', async () => {
    try{
      setLoading(true);
      notify('Testing connection...');
      currentApiBase = null;
      const base = await health();
      currentApiBase = base;
      notify('Connected: ' + base);
      const seedRes = await fetch(api('/api/seed'), { method: 'POST' });
      await ensureOk(seedRes);
      notify('Sample data loaded. Generating...');
      const body = { days: getDaysFromUI(), slots: DEFAULT_SLOTS };
      const resGen = await fetch(api('/api/generate'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      await ensureOk(resGen);
      const res = await fetch(api('/api/timetable'));
      await ensureOk(res);
      const items = await res.json();
      renderTable(items, body.days, body.slots);
      notify('Timetable generated');
    }catch(err){
      notify('Quick Run failed: ' + (err.message || String(err)), true);
    }finally{
      setLoading(false);
    }
  });

  daysPresetSelect?.addEventListener('change', () => {
    notify('Days preset set to: ' + daysPresetSelect.value);
  });

  uploadForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try{
      setLoading(true);
      const fd = new FormData(uploadForm);
      const res = await fetch(api('/api/upload'), { method: 'POST', body: fd });
      await ensureOk(res);
      await res.json();
      notify('Upload successful');
    }catch(err){
      notify(err.message || String(err), true);
    }finally{
      setLoading(false);
    }
  });

  generateBtn?.addEventListener('click', async () => {
    try{
      setLoading(true);
      const body = {
        days: getDaysFromUI(),
        slots: DEFAULT_SLOTS
      };
      const resGen = await fetch(api('/api/generate'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      await ensureOk(resGen);
      const res = await fetch(api('/api/timetable'));
      await ensureOk(res);
      const items = await res.json();
      renderTable(items, body.days, body.slots);
      notify('Timetable generated');
    }catch(err){
      notify(err.message || String(err), true);
    }finally{
      setLoading(false);
    }
  });

  function getApiBase(){
    const raw = (apiUrlInput?.value || '').trim().replace(/\/$/, '');
    return raw || detectApiBase();
  }

  function detectApiBase(){
    try{
      const { protocol, hostname } = window.location;
      const port = '8000';
      return `${protocol}//${hostname}:${port}`;
    }catch{
      return 'http://localhost:8000';
    }
  }

  function getBaseCandidates(){
    const typed = getApiBase();
    const list = new Set();
    const variants = (u) => {
      try{
        const url = new URL(u);
        const protos = url.protocol === 'https:' ? ['https:','http:'] : ['http:','https:'];
        const hosts = [url.hostname];
        if(url.hostname === 'localhost') hosts.push('127.0.0.1');
        if(url.hostname === '127.0.0.1') hosts.push('localhost');
        for(const p of protos){
          for(const h of hosts){
            list.add(`${p}//${h}${url.port ? ':'+url.port : ''}`);
          }
        }
      }catch{}
    };
    variants(typed);
    variants(detectApiBase());
    return Array.from(list);
  }

  async function health(){
    const bases = getBaseCandidates();
    let lastErr = null;
    for(const base of bases){
      try{
        const res = await timedFetch(`${base}/api/health`, { method: 'GET' }, 4000);
        await ensureOk(res);
        // Update input to the working base
        if(apiUrlInput) apiUrlInput.value = base;
        return base;
      }catch(err){ lastErr = err; }
    }
    throw lastErr || new Error('Failed to reach backend');
  }

  async function timedFetch(resource, options, ms){
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), ms);
    try{
      const res = await fetch(resource, { ...(options||{}), signal: controller.signal });
      return res;
    }finally{
      clearTimeout(id);
    }
  }

  function api(path){
    const base = currentApiBase || getApiBase();
    return `${base}${path}`;
  }

  async function ensureOk(res){
    if(!res.ok){
      let msg = `HTTP ${res.status}`;
      try{ const j = await res.json(); if(j && j.detail) msg += ` - ${j.detail}`; }catch{}
      throw new Error(msg);
    }
  }

  function notify(message, isError=false){
    const el = document.createElement('div');
    el.textContent = message;
    el.style.position = 'fixed';
    el.style.bottom = '16px';
    el.style.right = '16px';
    el.style.padding = '10px 14px';
    el.style.borderRadius = '8px';
    el.style.zIndex = '9999';
    el.style.color = 'white';
    el.style.background = isError ? '#dc2626' : '#16a34a';
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2500);
  }

  function setLoading(loading){
    if(loading){
      generateBtn.setAttribute('disabled', 'true');
    }else{
      generateBtn.removeAttribute('disabled');
    }
  }

  function getDaysFromUI(){
    const val = (daysPresetSelect?.value || 'Mon,Tue,Wed,Thu,Fri').trim();
    return val.split(',').map(x => x.trim()).filter(Boolean);
  }

  function renderTable(items, days, slots){
    const DAYS = days && days.length ? days : ['Mon','Tue','Wed','Thu','Fri'];
    const SLOTS = slots && slots.length ? slots : DEFAULT_SLOTS;

    timetableRoot.innerHTML = '';
    const grid = document.createElement('div');
    grid.className = 'grid';

    // Setup grid headers
    grid.append(cell('','header'));
    DAYS.forEach(d => grid.append(cell(d, 'header')));

    // Build a map day->slot->array of entries
    const map = new Map();
    for(const x of items){
      const k = `${x.day}|${x.slot}`;
      if(!map.has(k)) map.set(k, []);
      map.get(k).push(x);
    }

    SLOTS.forEach(slot => {
      grid.append(cell(slot, 'rowlabel'));
      DAYS.forEach(day => {
        const entries = map.get(`${day}|${slot}`) || [];
        if(entries.length === 0){
          grid.append(cell(''));
        }else{
          const c = document.createElement('div');
          c.className = 'cell';
          for(const e of entries){
            const block = document.createElement('div');
            block.style.border = '1px solid var(--border)';
            block.style.borderRadius = '6px';
            block.style.padding = '6px';
            block.style.marginBottom = '6px';
            block.style.background = '#0c1426';
            block.textContent = `${e.course}\n${e.section} | ${e.teacher}\nRoom: ${e.room}`;
            c.append(block);
          }
          grid.append(c);
        }
      });
    });
    timetableRoot.append(grid);
  }

  function cell(text, cls='cell'){
    const d = document.createElement('div');
    d.className = `cell ${cls}`;
    d.textContent = text;
    return d;
  }
})();
