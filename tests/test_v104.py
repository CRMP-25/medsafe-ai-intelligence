import networkx as nx
from reporting_v104 import markdown_report,build_evidence_graph,graphml_bytes,record_link

def sample():
    return {'drug':'buprenorphine','generated_utc':'2026-10-26T12:00:00Z','evidence':{
        'events':{'results':[{'term':'Nausea','count':25}],'url':'https://api.fda.gov/drug/event.json','total':None},
        'errors':{'results':[{'safetyreportid':'123','patient':{'reaction':[{'reactionmeddrapt':'Overdose'}]}}],'total':100,'url':'https://api.fda.gov/drug/event.json'},
        'labels':{'results':[{'id':'abc','openfda':{'brand_name':['Brand']},'boxed_warning':['Warning']}],'total':1,'url':'https://api.fda.gov/drug/label.json'},
        'recalls':{'results':[{'recall_number':'D-001-2026','reason_for_recall':'Sterility','status':'Ongoing'}],'total':1,'url':'https://api.fda.gov/drug/enforcement.json'}}}

def test_markdown_complete_and_caveats():
    report=markdown_report(sample())
    assert '100' in report and 'Overdose' in report and 'D-001-2026' in report
    assert 'causality' in report and 'FDA source' in report

def test_graph_hierarchy():
    g=build_evidence_graph(sample())
    assert g.has_edge('buprenorphine','Category: errors')
    assert g.has_edge('Category: errors','errors:123')
    assert not g.has_edge('buprenorphine','errors:123')
    assert len(g.nodes)==9

def test_graphml_export():
    content=graphml_bytes(build_evidence_graph(sample()))
    assert nx.parse_graphml(content.decode('utf-8')).number_of_nodes()==9

def test_filter_graph_layers():
    g=build_evidence_graph(sample(),selected=['recalls'])
    assert 'Category: labels' not in g and 'recalls:D-001-2026' in g

def test_record_links():
    assert 'safetyreportid' in record_link('errors',{'safetyreportid':'123'},'')
