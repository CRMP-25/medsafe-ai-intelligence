import math
import requests
import time
import networkx as nx
from datetime import datetime, timezone
BASE='https://api.fda.gov'
DRUGS=['buprenorphine','methadone','gabapentin','naloxone']
def fetch(endpoint, params):
    """Return provenance and provider totals; retry transient throttling only."""
    url=f'{BASE}/{endpoint}.json'
    headers={'User-Agent':'MedSafe-Intelligence/1.0 (educational demonstration)','Accept':'application/json'}
    for attempt in range(3):
        try:
            r=requests.get(url,params=params,timeout=25,headers=headers)
            if r.status_code in (429,500,502,503,504) and attempt<2:
                time.sleep(1.5*(attempt+1)); continue
            r.raise_for_status()
            payload=r.json()
            return {'results':payload.get('results',[]),'total':payload.get('meta',{}).get('results',{}).get('total'),
                    'url':r.url,'retrieved_utc':datetime.now(timezone.utc).isoformat()}
        except requests.RequestException:
            if attempt==2: raise
            raise

def annual_report_totals(drug, start_year=2018, end_year=None):
    """Yearly FAERS report totals, using API metadata rather than unsupported date counts.

    Each year is an independent bounded query; failed years are missing, never zero.
    """
    end_year=end_year or datetime.now(timezone.utc).year
    rows=[]; failures=[]
    for year in range(start_year,end_year+1):
        params={'search':f'patient.drug.medicinalproduct:"{drug}" AND receivedate:[{year}0101 TO {year}1231]','limit':1}
        try:
            result=fetch('drug/event',params)
            rows.append({'year':str(year),'report_count':result['total'],'url':result['url'],
                         'retrieved_utc':result['retrieved_utc']})
        except requests.RequestException as exc:
            failures.append({'year':year,'error':str(exc)})
    return {'results':rows,'failures':failures,'method':'Annual bounded FAERS query; meta.results.total; not incidence',
            'retrieved_utc':datetime.now(timezone.utc).isoformat()}

def events(drug, field='patient.drug.medicinalproduct', limit=15):
    return fetch('drug/event',{'search':f'{field}:"{drug}"','count':'patient.reaction.reactionmeddrapt.exact','limit':limit})
def trend(drug):
    return annual_report_totals(drug)
def labels(drug):
    return fetch('drug/label',{'search':f'openfda.generic_name:"{drug}"','limit':5})
def recalls(drug):
    return fetch('drug/enforcement',{'search':f'product_description:"{drug}"','limit':20})
def errors(drug):
    terms=['Medication error','Overdose','Incorrect dose administered','Wrong drug administered','Drug administration error','Product confusion']
    query=' OR '.join('patient.reaction.reactionmeddrapt:"'+term+'"' for term in terms)
    return fetch('drug/event',{'search':f'patient.drug.medicinalproduct:"{drug}" AND ('+query+')','limit':100})
def disproportionality(a,b,c,d):
    if not all(type(x) is int and x>=0 for x in (a,b,c,d)): raise ValueError('Nonnegative integer cells required')
    if a+b==0 or c+d==0 or a+c==0 or b+d==0: raise ValueError('Each row and column must contain at least one observed report')
    if min(a,b,c,d)==0: a,b,c,d=(x+.5 for x in (a,b,c,d)); correction=True
    else: correction=False
    ror=a*d/(b*c)
    se=math.sqrt(sum(1/x for x in (a,b,c,d)))
    prr=(a/(a+b))/(c/(c+d))
    return {'ROR':ror,'ROR_CI95_low':math.exp(math.log(ror)-1.96*se),'ROR_CI95_high':math.exp(math.log(ror)+1.96*se),'PRR':prr,'haldane_correction':correction}
def graph(drug, reactions, label_sections=None):
    g=nx.DiGraph();g.add_node(drug,kind='drug')
    for r in reactions:
        name=r['term'];g.add_node(name,kind='reported reaction');g.add_edge(drug,name,relation='reported with',count=r['count'],source='openFDA FAERS aggregate')
    for section in (label_sections or []):
        g.add_node(section,kind='label section');g.add_edge(drug,section,relation='FDA labeling section',source='openFDA drug label')
    return g
