"""Bounded, evidence-linked concept graph; no inferred biological causality."""
import hashlib
import networkx as nx
from reporting_v104 import record_link, clean

QUESTIONS=[
('Emerging signals','What emerging safety signals are associated with this medication?','events'),
('Regulatory gaps','Which reported events warrant checking against current regulatory warnings?','events,labels'),
('Vulnerable populations','Which patient groups are represented in available safety reports?','errors'),
('Unexpected diseases','Are unexpected conditions mentioned in reports or labels?','errors,labels'),
('Drug combinations','Which co-reported medicines occur in medication-error reports?','errors'),
('Trial versus real world','Do trial findings differ from spontaneous reporting patterns?','external evidence needed'),
('Warning timeline','Which reports predate a relevant FDA label warning?','errors,labels'),
('Shared mechanisms','Do events share established biological mechanisms?','external evidence needed'),
('Surprising paths','Which unusual multi-hop connections appear in retrieved evidence?','graph'),
('Alternatives','How do regulatory warnings differ across treatment alternatives?','external evidence needed'),
('Older patients','Which retrieved reports involve older adults?','errors'),
('New literature','Which new publications challenge existing safety assumptions?','external evidence needed'),
('Serious outcomes','Which retrieved reports mention hospitalization or death?','errors'),
('Off-label concerns','Are indications and reported use patterns inconsistent?','labels,errors'),
('Independent corroboration','Which associations have support from more than one source type?','graph'),
('Temporal changes','How have reporting counts changed across years?','trend'),
('Shared events','Which medicines are co-mentioned in reports of similar events?','errors'),
('Common pathways','What validated pathways might link different events?','external evidence needed'),
('Investigation priorities','Which reported patterns deserve further independent evaluation?','events,errors'),
('New hypotheses','What evidence-linked, unverified hypotheses can be generated?','graph')]

def concept_graph(inv, limit_per_kind=300):
    """Build shared concept nodes across retrieved evidence; do not imply causation."""
    g=nx.DiGraph(); drug=str(inv.get('drug','Medication'))
    root='drug:'+drug.casefold();g.add_node(root,kind='drug',label=drug)
    for kind,payload in (inv.get('evidence') or {}).items():
        if kind not in ('events','errors','labels','recalls') or not isinstance(payload,dict):continue
        source=payload.get('url','')
        for idx,row in enumerate((payload.get('results') or [])[:limit_per_kind]):
            if not isinstance(row,dict):continue
            rid=str(row.get('safetyreportid') or row.get('id') or row.get('recall_number') or row.get('term') or idx)
            record=f'record:{kind}:{rid}';g.add_node(record,kind='record',label=f'{kind}: {clean(rid,28)}',url=record_link(kind,row,source),source=source)
            g.add_edge(root,record,relation='retrieved for medication',source=source)
            concepts=[]
            if kind=='events' and row.get('term'):concepts.append(('event',row['term']))
            if kind=='errors':
                patient=row.get('patient') or {}
                for reaction in (patient.get('reaction') or [])[:12]:
                    if isinstance(reaction,dict) and reaction.get('reactionmeddrapt'):concepts.append(('event',reaction['reactionmeddrapt']))
                for medication in (patient.get('drug') or [])[:12]:
                    if isinstance(medication,dict) and medication.get('medicinalproduct'):concepts.append(('reported_medicine',medication['medicinalproduct']))
            if kind=='labels':
                for name in ((row.get('openfda') or {}).get('generic_name') or [])[:4]:concepts.append(('label_medicine',name))
                for section in ('boxed_warning','warnings','contraindications'):
                    if row.get(section):concepts.append(('label_section',section.replace('_',' ')))
            if kind=='recalls' and row.get('reason_for_recall'):concepts.append(('recall_reason',clean(row['reason_for_recall'],110)))
            for typ,value in concepts:
                label=clean(value,110)
                if not label:continue
                key=typ+':'+hashlib.sha256(label.casefold().encode()).hexdigest()[:20]
                g.add_node(key,kind=typ,label=label)
                g.add_edge(record,key,relation='mentioned in source record',source=source)
    return g

def bounded_view(g,focus=None,hops=2,max_nodes=90):
    if not len(g):return g.copy()
    focus=focus if focus in g else next(iter(g))
    undirected=g.to_undirected();dist=nx.single_source_shortest_path_length(undirected,focus,cutoff=hops)
    selected=sorted(dist,key=lambda n:(dist[n],-undirected.degree(n),str(n)))[:max_nodes]
    return g.subgraph(selected).copy()

def paths(g,start,end,max_hops=6,max_paths=8):
    if start not in g or end not in g or start==end:return []
    try:
        return list(__import__('itertools').islice(nx.all_simple_paths(g.to_undirected(),start,end,cutoff=max_hops),max_paths))
    except (nx.NetworkXNoPath,nx.NodeNotFound):return []
