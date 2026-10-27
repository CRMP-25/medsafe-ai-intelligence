"""Complete investigation export; no truncation of evidence IDs."""
import csv
import io
import json
import zipfile
from collections import Counter
from datetime import datetime, timezone
from html import escape
import networkx as nx
from semantic_v106 import associations, export_bundle
from reporting_v104 import markdown_report, graphml_bytes

def _csv(rows):
    output=io.StringIO()
    if rows:
        writer=csv.DictWriter(output,fieldnames=list(rows[0]),extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    return output.getvalue()

def complete_report_zip(inv,g,drug):
    pairs=associations(g)
    nodes=[{'id':n,**d} for n,d in g.nodes(data=True)]
    edges=[{'from':a,'to':b,**d} for a,b,d in g.edges(data=True)]
    types=dict(Counter(d.get('kind','unknown') for _,d in g.nodes(data=True)))
    sources=dict(Counter(d.get('source_kind','unknown') for _,d in g.nodes(data=True) if d.get('kind')=='record'))
    manifest={'schema':'medsafe-complete-report-v1','application_version':'1.0.10-testing','drug':drug,'created_utc':datetime.now(timezone.utc).isoformat(),
              'nodes':len(nodes),'edges':len(edges),'associations':len(pairs),'node_types':types,'record_sources':sources,
              'retrieval_audit':__import__('intelligence_v110').retrieval_audit(inv),
              'limitations':['FAERS co-reporting is not causation or incidence.','Only retrieved evidence is included; API retrieval may be incomplete.','Graph and association counts are not risk estimates.']}
    top=pairs[:50]
    trs=''.join('<tr>'+''.join('<td>'+escape(str(row.get(k,'')))+'</td>' for k in ('concept_a','concept_b','co_reported_records'))+'</tr>' for row in top)
    html='<!doctype html><html><head><meta charset="utf-8"><title>MedSafe Complete Investigation</title><style>body{font-family:Arial,sans-serif;max-width:1100px;margin:35px auto;line-height:1.5}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:7px;text-align:left}th{background:#e8f0f5}</style></head><body><h1>MedSafe Complete Investigation: '+escape(drug)+'</h1><p><b>Evidence limitations:</b> Co-mentions are not causal or incidence estimates. All counts are limited to retrieved records.</p><p>Nodes: '+str(len(nodes))+' | Edges: '+str(len(edges))+' | Co-mention associations: '+str(len(pairs))+'</p><h2>Record source distribution</h2><pre>'+escape(json.dumps(sources,indent=2))+'</pre><h2>Top 50 co-mentions (noncausal)</h2><table><tr><th>Concept A</th><th>Concept B</th><th>Supporting records</th></tr>'+trs+'</table><p>See associations.csv for ALL pairs and ALL source IDs/URLs; evidence_records.csv for individual records; semantic_graph.json and semantic_graph.graphml for the full graph.</p></body></html>'
    records=[{'graph_id':n,'source_kind':d.get('source_kind',''),'source_id':d.get('source_id',''),'source_url':d.get('source_url','')} for n,d in g.nodes(data=True) if d.get('kind')=='record']
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,'w',compression=zipfile.ZIP_DEFLATED) as z:
        files={'manifest.json':json.dumps(manifest,indent=2),'investigation.json':json.dumps(inv,indent=2,default=str),
               'normalization_review.json':json.dumps(__import__('intelligence_v109').canonical_groups(g),indent=2),
               'semantic_graph.json':export_bundle(g,drug),'semantic_graph.graphml':graphml_bytes(g),
               'associations.csv':_csv(pairs),'evidence_records.csv':_csv(records),
               'graph_nodes.csv':_csv(nodes),'graph_edges.csv':_csv(edges),
               'investigation_report.md':markdown_report(inv),'complete_report.html':html}
        for name,content in files.items():z.writestr(name,content)
    return mem.getvalue()
