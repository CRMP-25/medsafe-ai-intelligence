from semantic_v106 import semantic_graph, associations, export_bundle, import_bundle, merge_graphs

def sample():
    return {'drug':'buprenorphine','evidence':{'errors':{'url':'https://api.fda.gov/drug/event.json','results':[{'safetyreportid':'123','patient':{'reaction':[{'reactionmeddrapt':'Overdose'},{'reactionmeddrapt':'Drug dependence'}],'drug':[{'medicinalproduct':'Buprenorphine'}]}}]}}}

def test_co_mentions_and_source():
    g=semantic_graph(sample()); rows=associations(g)
    assert any({r['concept_a'],r['concept_b']}=={'Overdose','Drug dependence'} for r in rows)
    assert any('safetyreportid' in r['source_urls'] for r in rows)
    assert all(r['causal_inference']=='NOT ESTABLISHED' for r in rows)

def test_bundle_roundtrip_and_merge():
    g=semantic_graph(sample()); restored=import_bundle(export_bundle(g,'buprenorphine'))
    assert len(restored)==len(g)
    assert merge_graphs(g,restored).number_of_edges()==g.number_of_edges()
