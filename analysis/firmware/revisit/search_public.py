import urllib.request,urllib.parse,json,re,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
queries=['"line6" firmware','"L6FF"','"spider" "line 6"','"Spider V" amplifier','line6 decrypt']
results=[]
for i,q in enumerate(queries):
 url='https://github.com/search?'+urllib.parse.urlencode({'q':q,'type':'repositories'})
 row={'query':q,'url':url}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=20)as response:b=response.read();row['status']=response.status
  name=f'public_search_{i}.html';(OUT/name).write_bytes(b);row['source']=name;row['sha256']=hashlib.sha256(b).hexdigest()
  for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',b.decode(),re.S):
   try:d=json.loads(m.group(1))
   except Exception:continue
   payload=d.get('payload',{});route=payload.get('blackbirdSearchRoute',payload)
   if 'results'in route and 'result_count'in route:
    row['result_count']=route['result_count'];row['results']=[{'name':r.get('hl_name'),'description':r.get('hl_trunc_description'),'repo':r.get('repo')}for r in route['results']];break
 except Exception as e:row['error']=str(e)
 results.append(row);print(json.dumps(row,ensure_ascii=False)[:2000])
(OUT/'public_sources.json').write_text(json.dumps(results,indent=2)+'\n')
