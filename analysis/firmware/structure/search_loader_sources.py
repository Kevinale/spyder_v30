import urllib.request,urllib.parse,re,json,concurrent.futures
from pathlib import Path
out=Path(__file__).resolve().parent
queries=['BF707','line6 firmware decrypt','line6 firmware','Blackfin loader','L6FF']
def search(q):
 row={'query':q};url='https://github.com/search?'+urllib.parse.urlencode({'q':q,'type':'repositories'});row['url']=url
 try:
  data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read().decode()
  for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',data,re.S):
   try:d=json.loads(m.group(1)).get('payload',{});route=d.get('blackbirdSearchRoute',d)
   except ValueError:continue
   if 'results' in route:
    row['count']=route.get('result_count');row['results']=[{'name':r.get('hl_name'),'description':r.get('hl_trunc_description')} for r in route['results']];break
 except Exception as e:row['error']=str(e)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:rows=list(e.map(search,queries))
(out/'loader_sources_search.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
