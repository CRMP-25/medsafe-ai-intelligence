"""V1.0.6: conservative, source-grounded semantic graph and portable persistence."""
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
import networkx as nx
from reporting_v104 import record_link, clean

SCHEMA = 'medsafe-semantic-v1'

def _key(kind, value):
    normalized = re.sub(r'\s+', ' ', str(value or '').strip()).casefold()
    return kind + ':' + hashlib.sha256(normalized.encode()).hexdigest()[:20]

def _node(g, kind, value):
    label = clean(value, 150)
    if not label: return None
    key = _key(kind, label)
    if key not in g: g.add_node(key, kind=kind, label=label)
    return key

def _edge(g, a, b, relation, url='', record_id='', evidence_type='record_mention'):
    if not a or not b or a == b: return
    if g.has_edge(a,b):
        d=g[a][b]
        ids=set(filter(None,d.get('record_ids','').split('|')))
        if record_id: ids.add(str(record_id))
        d['record_ids']='|'.join(sorted(ids))
        d['supporting_records']=len(ids)
    else:
        g.add_edge(a,b,relation=relation,source_url=url or '',record_ids=str(record_id or ''),
                   supporting_records=1 if record_id else 0,evidence_type=evidence_type,
                   interpretation='co-mentioned or indexed; causality not established')

def semantic_graph(inv, limit_per_kind=500):
    g=nx.DiGraph()
    drug=clean(inv.get('drug','Medication'),150)
    root=_node(g,'drug',drug)
    for kind,payload in (inv.get('evidence') or {}).items():
        if kind not in ('events','errors','labels','recalls') or not isinstance(payload,dict): continue
        source=payload.get('url','')
        for i,row in enumerate((payload.get('results') or [])[:limit_per_kind]):
            if not isinstance(row,dict):continue
            rid=str(row.get('safetyreportid') or row.get('id') or row.get('recall_number') or row.get('term') or i)
            url=record_link(kind,row,source)
            rec=_node(g,'record',f'{kind}: {rid}')
            g.nodes[rec].update(source_url=url,source_kind=kind,source_id=rid)
            _edge(g,root,rec,'retrieved_for_drug',url,rid,'retrieval')
            concepts=[]
            if kind=='events' and row.get('term'):
                concepts.append(('adverse_event',row['term']))
            if kind=='errors':
                patient=row.get('patient') or {}
                for reaction in (patient.get('reaction') or [])[:30]:
                    if isinstance(reaction,dict) and reaction.get('reactionmeddrapt'):
                        concepts.append(('adverse_event',reaction['reactionmeddrapt']))
                for med in (patient.get('drug') or [])[:30]:
                    if isinstance(med,dict) and med.get('medicinalproduct'):
                        concepts.append(('reported_medication',med['medicinalproduct']))
                if patient.get('patientonsetage') is not None:
                    concepts.append(('reported_age',str(patient['patientonsetage'])+' (unit '+str(patient.get('patientonsetageunit','unknown'))+')'))
                if patient.get('patientsex') is not None:
                    concepts.append(('reported_sex_code',str(patient['patientsex'])))
                for flag, label in [('seriousnessdeath','death'),('seriousnesshospitalization','hospitalization')]:
                    if str(row.get(flag,''))=='1': concepts.append(('serious_outcome',label))
            if kind=='labels':
                for name in ((row.get('openfda') or {}).get('generic_name') or [])[:8]:
                    concepts.append(('label_medication',name))
                for section in ('boxed_warning','warnings','contraindications'):
                    if row.get(section):concepts.append(('label_section',section.replace('_',' ')))
            if kind=='recalls' and row.get('reason_for_recall'):
                concepts.append(('recall_reason',clean(row['reason_for_recall'],150)))
            for typ,value in concepts:
                concept=_node(g,typ,value)
                _edge(g,rec,concept,'record_mentions',url,rid)
    return g

def associations(g, min_records=1):
    """Pairs of concepts co-mentioned in a single source record, never causal edges."""
    counts=Counter(); examples={}
    for record,data in g.nodes(data=True):
        if data.get('kind')!='record' or data.get('source_kind')!='errors':continue
        neighbors=sorted(n for n in g.successors(record) if g.nodes[n].get('kind')!='record')
        for i,a in enumerate(neighbors):
            for b in neighbors[i+1:]:
                pair=(a,b);counts[pair]+=1
                examples.setdefault(pair,[]).append((data.get('source_id',''),data.get('source_url','')))
    result=[]
    for (a,b),count in counts.most_common():
        if count<min_records:continue
        result.append({'concept_a':g.nodes[a]['label'],'type_a':g.nodes[a]['kind'],
                       'concept_b':g.nodes[b]['label'],'type_b':g.nodes[b]['kind'],
                       'co_reported_records':count,'evidence_type':'within-record co-mention',
                       'causal_inference':'NOT ESTABLISHED',
                       'source_ids':', '.join(x[0] for x in examples[(a,b)]),
                       'source_urls':' | '.join(x[1] for x in examples[(a,b)])})
    return result

def export_bundle(g, drug):
    return json.dumps({'schema':SCHEMA,'drug':drug,'exported_utc':datetime.now(timezone.utc).isoformat(),
                       'nodes':[{'id':n,**d} for n,d in g.nodes(data=True)],
                       'edges':[{'from':a,'to':b,**d} for a,b,d in g.edges(data=True)]},indent=2)

def import_bundle(data):
    if isinstance(data,(bytes,str)):data=json.loads(data)
    if data.get('schema')!=SCHEMA:raise ValueError('Unsupported MedSafe graph bundle schema')
    g=nx.DiGraph()
    for n in data.get('nodes',[]):
        if not isinstance(n,dict) or 'id' not in n:raise ValueError('Invalid node')
        g.add_node(n['id'],**{k:v for k,v in n.items() if k!='id'})
    for e in data.get('edges',[]):
        if not isinstance(e,dict) or e.get('from') not in g or e.get('to') not in g:raise ValueError('Invalid edge endpoints')
        g.add_edge(e['from'],e['to'],**{k:v for k,v in e.items() if k not in ('from','to')})
    return g

def merge_graphs(previous, current):
    merged=previous.copy()
    for n,d in current.nodes(data=True):
        if n not in merged:merged.add_node(n,**d)
        else:merged.nodes[n].update(d)
    for a,b,d in current.edges(data=True):
        if not merged.has_edge(a,b):merged.add_edge(a,b,**d)
        else:
            old=merged[a][b]
            ids=set(filter(None,old.get('record_ids','').split('|')))|set(filter(None,d.get('record_ids','').split('|')))
            old.update(d);old['record_ids']='|'.join(sorted(ids));old['supporting_records']=len(ids)
    return merged
