#!/usr/bin/env python3
"""IRIAM public notice indexer. Follow relevant first-party article links, conservatively."""
import datetime, json, pathlib, re, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
BASE='https://info.iriam.com/イベントキャンペーン等お知らせ'
OUT=pathlib.Path(__file__).resolve().parents[1]/'data'/'official_news.json'
S=requests.Session(); S.headers.update({'User-Agent':'Mozilla/5.0 (compatible; IRIAMNoticeIndexer/2.0)'})
DATE=re.compile(r'(20\d{2})[年/.-]\s*(1[0-2]|0?[1-9])[月/.-]\s*(3[01]|[12]\d|0?[1-9])日?')
HEADING=re.compile(r'集計対象ギフト|指定ギフト|対象となるギフト|対象ギフト')
REWARD=re.compile(r'特典|プレゼント|獲得|配布|もらえる|贈呈')
GIFT_WORD=re.compile(r'ギフト')
STOP=re.compile(r'注意事項|参加条件|対象期間|開催期間|応募方法|ランキング|特典|問い合わせ|キャンペーン概要')
BAD=re.compile(r'対象ギフト|対象となるギフト|ギフト一覧|ギフトを|ポイント|pt|配信|イベント|ランキング|タブ|画像|こちら|詳細|注意|確認|ギフトが|ギフトの|ギフトは')
def soup_for(url):
 r=S.get(url,timeout=18);r.raise_for_status();return BeautifulSoup(r.text,'html.parser')
def official(url):return urlsplit(url).scheme=='https' and urlsplit(url).netloc=='info.iriam.com'
def inspect(url, depth=0, seen=None):
 seen=seen or set()
 if url in seen:return {'gifts':[],'sources':[],'evidence':[],'start':None,'end':None,'note':''}
 seen.add(url)
 try:soup=soup_for(url)
 except requests.RequestException:return {'gifts':[],'sources':[],'evidence':[],'start':None,'end':None,'note':'記事の取得に失敗'}
 for tag in soup.select('script,style,nav,footer,header'):tag.decompose()
 main=soup.select_one('article') or soup.select_one('main') or soup
 paragraphs=[x.get_text(' ',strip=True) for x in main.select('h1,h2,h3,h4,p,li')]
 gifts=[];sources=[];evidence=[];start=end=None;image_only=False
 for i,p in enumerate(paragraphs):
  if HEADING.search(p) and len(p)<110 and not REWARD.search(p):
   values=[]
   for v in paragraphs[i+1:i+9]:
    if STOP.search(v) and not HEADING.search(v):break
    candidate=re.sub(r'^[・●\-\s]+','',v).strip('「」『』【】 \t')
    if 2<=len(candidate)<=38 and not BAD.search(candidate) and not REWARD.search(candidate) and not re.search(r'[。！？:：]',candidate):values.append(candidate)
   gifts.extend(values)
   evidence.extend({'name':v,'url':url,'heading':p[:100]} for v in values)
   if not values:image_only=True
  if re.search(r'^(開催期間|実施期間|イベント期間)',p):
   dates=DATE.findall(' '.join(paragraphs[i:i+3]));ds=[]
   for y,m,d in dates:
    try:ds.append(datetime.date(int(y),int(m),int(d)).isoformat())
    except ValueError:pass
   if len(ds)>=2 and ds[0]<=ds[1] and not start:start,end=ds[:2]
 if gifts:sources.append(url)
 # Follow only explicitly related first-party detail pages, maximum 3; not arbitrary site-wide links.
 if depth==0:
  links=[]
  for a in main.select('a[href]'):
   href=urljoin(url,a['href']).split('#')[0];label=a.get_text(' ',strip=True)
   if official(href) and href!=url and href not in seen and re.search(r'詳細|対象ギフト|ギフト一覧|こちら|キャンペーン|ランキング',label):
    if href not in links:links.append(href)
  for href in links[:3]:
   child=inspect(href,1,seen)
   gifts.extend(child['gifts']);sources.extend(child['sources']);evidence.extend(child['evidence'])
   if not start and child['start']:start,end=child['start'],child['end']
 note='画像のみの掲載やアプリ内限定情報は自動判定できません。' if image_only else ''
 return {'gifts':list(dict.fromkeys(gifts))[:30],'sources':list(dict.fromkeys(sources)),'evidence':list({(v['name'],v['url']):v for v in evidence}.values())[:30],'start':start,'end':end,'note':note}
def main():
 soup=soup_for(BASE);items=[];seen=set()
 for a in soup.select('a[href]'):
  title=a.get_text(' ',strip=True);url=urljoin(BASE,a['href']).split('#')[0]
  if not official(url) or url.rstrip('/')==BASE.rstrip('/') or not 5<=len(title)<=160:continue
  if not any(k in title for k in ('IRIAM','イベント','キャンペーン','ミライト','甲子園','アンバサダー','コンテスト','周年')):continue
  if url in seen:continue
  seen.add(url);details=inspect(url)
  items.append({'title':title,'url':url,'category':'お知らせ','published':'','gift_status':'candidate' if details['gifts'] else 'unverified',**details})
  if len(items)>=60:break
 if not items:raise RuntimeError('No notices: preserving previous dataset')
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps({'source':BASE,'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'items':items},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Updated',len(items),'notices,',sum(bool(x['gifts']) for x in items),'with textual gift candidates')
if __name__=='__main__':main()
