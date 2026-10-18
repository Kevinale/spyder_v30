from pathlib import Path
import urllib.request,urllib.parse,concurrent.futures,json,re,hashlib
R=Path(__file__).resolve().parent
jobs=[('board485','"35-00-0485"'),('board487','"35-00-0487"'),('a39','"A39" "Line6"'),('nanya','NT5TU32M16FG'),('winbond','W25Q256FV')]
def run(j):
 label,q=j;url='https://github.com/search?'+urllib.parse.urlencode({'q':q,'type':'repositories'});row={'query':q,'url':url}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=12)as x:b=x.read();row['status']=x.status
  (R/('search_'+label+'.html')).write_bytes(b);row['sha256']=hashlib.sha256(b).hexdigest()
  for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',b.decode(),re.S):
   try:d=json.loads(m[1])
   except ValueError:continue
   p=d.get('payload',{});p=p.get('blackbirdSearchRoute',p)
   if 'results'in p and 'result_count'in p:row['count']=p['result_count'];row['results']=[{'name':z.get('hl_name'),'description':z.get('hl_trunc_description')}for z in p['results']];break
 except Exception as e:row['error']=str(e)
 return row
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(run,jobs));(R/'part_search.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
