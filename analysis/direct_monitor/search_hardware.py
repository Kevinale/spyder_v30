"""Read-only public repository search; no downloaded code execution."""
from pathlib import Path
import urllib.request,urllib.parse,json,re,hashlib
r=Path(__file__).resolve().parent;rows=[]
for i,q in enumerate(['"Spider V" hardware','"Spider V30"','"Spider V" teardown']):
 url='https://github.com/search?'+urllib.parse.urlencode({'q':q,'type':'repositories'});row={'query':q,'url':url}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=12) as x:b=x.read();row['status']=x.status
  (r/f'hardware_search_{i}.html').write_bytes(b);row['sha256']=hashlib.sha256(b).hexdigest()
  for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',b.decode(),re.S):
   try:d=json.loads(m[1])
   except ValueError:continue
   p=d.get('payload',{});p=p.get('blackbirdSearchRoute',p)
   if 'result_count' in p and 'results' in p:
    row['count']=p['result_count'];row['results']=[{'name':z.get('hl_name'),'description':z.get('hl_trunc_description')}for z in p['results']];break
 except Exception as e:row['error']=str(e)
 rows.append(row)
(r/'hardware_search.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
