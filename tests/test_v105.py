from intelligence_v105 import QUESTIONS,concept_graph,bounded_view,paths

def test_questions():
    assert len(QUESTIONS)==20

def test_shared_concept_and_paths():
    inv={'drug':'sample','evidence':{'errors':{'url':'https://example.org','results':[{'safetyreportid':'1','patient':{'reaction':[{'reactionmeddrapt':'Nausea'}]}},{'safetyreportid':'2','patient':{'reaction':[{'reactionmeddrapt':'Nausea'}]}}]}}}
    g=concept_graph(inv)
    terms=[n for n,d in g.nodes(data=True) if d.get('kind')=='event']
    assert len(terms)==1
    assert len(paths(g,'record:errors:1','record:errors:2'))>=1
    assert bounded_view(g,'record:errors:1',2,3).number_of_nodes()<=3
