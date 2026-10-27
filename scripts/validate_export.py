"""Offline MedSafe report ZIP structural/provenance validator.
Usage: python scripts/validate_export.py report.zip
       python scripts/validate_export.py --self-test
"""
import argparse
import csv
import io
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

# Allow direct execution from the repository root or any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from xml.etree import ElementTree as ET

REQUIRED = {'manifest.json', 'investigation.json', 'semantic_graph.json',
            'semantic_graph.graphml', 'associations.csv', 'evidence_records.csv',
            'graph_nodes.csv', 'graph_edges.csv', 'investigation_report.md',
            'complete_report.html'}

def check(data):
    errors=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        bad=z.testzip()
        if bad: errors.append(f'ZIP CRC failed: {bad}')
        missing=REQUIRED-set(z.namelist())
        if missing: errors.append(f'Missing files: {sorted(missing)}')
        if missing: return errors
        manifest=json.loads(z.read('manifest.json'))
        graph=json.loads(z.read('semantic_graph.json'))
        json.loads(z.read('investigation.json'))
        nodes=graph['nodes']; edges=graph['edges']
        ids={n['id'] for n in nodes}
        if len(ids)!=len(nodes): errors.append('Duplicate node IDs')
        for edge in edges:
            if edge['from'] not in ids or edge['to'] not in ids:
                errors.append('Edge references unknown node'); break
        for key,actual in [('nodes',len(nodes)),('edges',len(edges))]:
            if manifest.get(key)!=actual: errors.append(f'Manifest {key} mismatch')
        assoc=list(csv.DictReader(io.StringIO(z.read('associations.csv').decode('utf-8'))))
        if manifest.get('associations')!=len(assoc):errors.append('Manifest associations mismatch')
        node_by_id={n['id']:n for n in nodes}
        concepts=defaultdict(set)
        for edge in edges:
            a,b=edge['from'],edge['to']
            if node_by_id[a].get('kind')=='record' and node_by_id[b].get('kind')!='record':
                concepts[a].add(b)
            elif node_by_id[b].get('kind')=='record' and node_by_id[a].get('kind')!='record':
                concepts[b].add(a)
        record_index=defaultdict(set)
        for record,concept_ids in concepts.items():
            if node_by_id[record].get('source_kind')!='errors':continue
            from itertools import combinations
            for pair in combinations(sorted(concept_ids),2):record_index[pair].add(record)
        # Association exports are deliberately restricted to medication-error evidence.
        key_index=defaultdict(list)
        for n in nodes:
            key_index[(n.get('kind'),n.get('label'))].append(n['id'])
        for i,row in enumerate(assoc):
            count=int(row['co_reported_records'])
            sources=[s.strip() for s in row['source_ids'].split(', ') if s.strip()]
            urls=[s.strip() for s in row['source_urls'].split(' | ') if s.strip()]
            if count!=len(sources) or count!=len(urls):
                errors.append(f'Association row {i+1}: truncated provenance');break
            a=key_index.get((row['type_a'],row['concept_a']),[])
            b=key_index.get((row['type_b'],row['concept_b']),[])
            if len(a)==1 and len(b)==1:
                records=record_index.get(tuple(sorted((a[0],b[0]))),set())
                expected={str(node_by_id[r].get('source_id','')) for r in records}
                if count!=len(records) or set(sources)!=expected:
                    errors.append(f'Association row {i+1}: graph provenance mismatch');break
        root=ET.fromstring(z.read('semantic_graph.graphml'))
        ns={'g':'http://graphml.graphdrawing.org/xmlns'}
        xml_nodes=root.findall('.//g:node',ns)
        xml_edges=root.findall('.//g:edge',ns)
        if len(xml_nodes)!=len(nodes) or len(xml_edges)!=len(edges):
            errors.append('GraphML node/edge count mismatch')
        xml_ids={x.attrib['id'] for x in xml_nodes}
        if any(e.attrib.get('source') not in xml_ids or e.attrib.get('target') not in xml_ids for e in xml_edges):
            errors.append('GraphML has dangling edges')
    return errors

def self_test():
    import networkx as nx
    from reporting_v107 import complete_report_zip
    g=nx.DiGraph()
    g.add_node('a',kind='adverse_event',label='A')
    g.add_node('b',kind='adverse_event',label='B')
    for i in range(12):
        r=f'r{i}'
        g.add_node(r,kind='record',source_kind='errors',source_id=str(i),source_url=f'https://example.org/{i}')
        g.add_edge(r,'a',relation='record_mentions')
        g.add_edge(r,'b',relation='record_mentions')
    return complete_report_zip({'drug':'test','evidence':{}},g,'test')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('zipfile',nargs='?')
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if not args.self_test and not args.zipfile:parser.error('Provide ZIP path or --self-test')
    data=self_test() if args.self_test else Path(args.zipfile).read_bytes()
    problems=check(data)
    if problems:
        print('FAILED:',*problems,sep='\n- ')
        sys.exit(1)
    print('PASS: ZIP, graph, GraphML, counts, and full association provenance')
