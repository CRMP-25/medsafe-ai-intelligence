import math
import requests
import networkx as nx
from datetime import datetime, timezone
BASE='https://api.fda.gov'
DRUGS=['buprenorphine','methadone','gabapentin','naloxone']
def fetch(endpoint, params):
    r=requests.get(f'{BASE}/{endpoint}.json',params=params,timeout=20,headers={'User-Agent':'MedSafe-Intelligence/1.0 educational demo'})
    r.raise_for_status()
    return {'results':r.json().get('results',[]),'url':r.url,'retrieved_utc':datetime.now(timezone.utc).isoformat()}
def events(drug, field='patient.drug.medicinalproduct', limit=15):
    return fetch('drug/event',{'search':f'{field}:"{drug}"','count':'patient.reaction.reactionmeddrapt.exact','limit':limit})
def trend(drug):
    return fetch('drug/event',{'search':f'patient.drug.medicinalproduct:"{drug}"','count':'receivedate','limit':1000})
def labels(drug):
    return fetch('drug/label',{'search':f'openfda.generic_name:"{drug}"','limit':5})
def recalls(drug):
    return fetch('drug/enforcement',{'search':f'product_description:"{drug}"','limit':20})
def errors(drug):
    terms=['Medication error','Overdose','Incorrect dose administered','Wrong drug administered','Drug administration error','Product confusion']
    query=' OR '.join('patient.reaction.reactionmeddrapt:"'+term+'"' for term in terms)
    return fetch('drug/event',{'search':f'patient.drug.medicinalproduct:"{drug}" AND ('+query+')','limit':100})
def disproportionality(a,b,c,d):
    if min(a,b,c,d)<0 or not all(isinstance(x,int) for x in (a,b,c,d)): raise ValueError('Nonnegative integer cells required')
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
