from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
APP_NAME='Deep Search OSINT Dashboard'
DB_FILE=Path(__file__).resolve().parent.parent/'data'/'app.sqlite'
DB_FILE.parent.mkdir(exist_ok=True)
app=FastAPI(title=APP_NAME, version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
def db() -> sqlite3.Connection:
    conn=sqlite3.connect(DB_FILE); conn.row_factory=sqlite3.Row; conn.execute('pragma journal_mode=wal'); return conn
def init_db() -> None:
    with db() as conn: conn.execute('create table if not exists records (id integer primary key autoincrement, kind text not null, title text not null, payload text not null, created_at text not null)')
@app.on_event("startup")
def on_startup() -> None:
    init_db()
def save_record(kind: str, title: str, payload: str) -> int:
    with db() as conn:
        cur=conn.execute('insert into records(kind,title,payload,created_at) values (?,?,?,?)',(kind,title,payload,datetime.now(timezone.utc).isoformat())); return int(cur.lastrowid)
def rows(kind: str | None = None) -> list[dict[str, Any]]:
    with db() as conn:
        data=conn.execute('select * from records where kind=? order by id desc',(kind,)).fetchall() if kind else conn.execute('select * from records order by id desc').fetchall()
    return [dict(r) for r in data]
@app.get('/api/health')
def health(): return {'ok': True, 'app': APP_NAME, 'records': len(rows())}
@app.get('/', response_class=HTMLResponse)
def home(): return INDEX_HTML

class DomainRequest(BaseModel):
    domain: str = Field(..., min_length=3)
def rdap_lookup(domain: str) -> dict:
    try:
        import urllib.request
        resp = urllib.request.urlopen(urllib.request.Request(f"https://rdap.verisign.com/com/v1/domain/{domain}", headers={"Accept":"application/rdap+json","User-Agent":"osint-dash/0.1"}), timeout=10)
        data = json.loads(resp.read().decode())
        return {"registrar": data.get('events',[{}])[0].get('eventAction','N/A'), "creation_date": next((e['eventDate'][:10] for e in data.get('events',[]) if e.get('eventAction')=='registration'),'N/A'), "expiry_date": next((e['eventDate'][:10] for e in data.get('events',[]) if e.get('eventAction')=='expiration'),'N/A'), "nameservers": [ns.get('ldhName','') for ns in data.get('nameservers',[])]}
    except Exception as e:
        return {"error": str(e)[:120]}
def dns_records(domain: str) -> dict:
    records = {"a":[], "mx":[], "ns":[], "txt":[]}
    try:
        import subprocess
        for rtype in ['A','MX','NS','TXT']:
            r = subprocess.run(['nslookup','-type='+rtype,domain], capture_output=True, text=True, timeout=10)
            for line in r.stdout.splitlines():
                s=line.strip()
                if '=' in s:
                    val=s.split('=',1)[-1].strip()
                    if val: records[rtype.lower()].append(val)
    except Exception:
        records["note"] = "DNS lookup unavailable"
    return records
@app.post('/api/lookup')
def lookup(req: DomainRequest):
    domain = req.domain.lower().strip()
    rdap = rdap_lookup(domain)
    dns = dns_records(domain)
    result = {"domain": domain, "whois": rdap, "dns": dns}
    save_record('lookup', domain, json.dumps(result))
    return result
@app.get('/api/history')
def history():
    return {"lookups": [json.loads(r['payload']) | {'id':r['id'],'created_at':r['created_at']} for r in rows('lookup')]}

INDEX_HTML='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Deep Search OSINT Dashboard</title><style>body{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#e5e7eb;margin:0}main{max-width:980px;margin:auto;padding:32px}.card{background:#111827;border:1px solid #334155;border-radius:18px;padding:24px;margin:18px 0}h1{font-size:42px}textarea,input{width:100%;box-sizing:border-box;border-radius:12px;border:1px solid #475569;background:#020617;color:#e5e7eb;padding:14px;margin:8px 0}button{background:#22c55e;color:#04130a;border:0;border-radius:12px;padding:12px 18px;font-weight:700}pre{white-space:pre-wrap;background:#020617;border-radius:12px;padding:16px}.pill{background:#1e293b;border:1px solid #475569;border-radius:999px;padding:6px 10px}</style></head><body><main><div class="card"><span class="pill">security research</span><h1>Deep Search OSINT Dashboard</h1><p>Passive domain reconnaissance: subdomains, WHOIS, DNS records, metadata, and clean investigative reports.</p><ul><li>Domain/company passive search</li><li>WHOIS metadata lookup</li><li>DNS record inspection</li><li>Report generation (markdown/PDF)</li><li>Export findings to file</li></ul></div><div class="card"><h2>Live Demo</h2><textarea id="input" rows="6">example.com</textarea><button onclick="runDemo()">Run</button><pre id="out">Click Run to call the API.</pre></div><div class="card"><h2>API</h2><p>Health: /api/health &middot; Docs: /docs</p></div><script>async function runDemo(){const res=await (fetch(\'/api/lookup\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({domain:document.getElementById(\'input\').value})}));document.getElementById(\'out\').textContent=JSON.stringify(await res.json(),null,2);}</script></main></body></html>'
