import io, json, zipfile
import networkx as nx
from intelligence_v110 import display_label, display_association, retrieval_audit
from reporting_v107 import complete_report_zip

def test_labels_preserve_original():
    row={'concept_a':'OVERDOSE','type_a':'adverse_event','concept_b':'1','type_b':'reported_sex_code','co_reported_records':148}
    new=display_association(row)
    assert 'Male' in new['concept_b'] and row['concept_b']=='1'
    assert display_label('BUPRENORPHINE.', 'reported_medication') == 'BUPRENORPHINE'
    assert 'Unrecognized' in display_label('9','reported_sex_code')

def test_retrieval_audit():
    a=retrieval_audit({'evidence':{'errors':{'results':[{},{}], 'total':10,'complete':False,'pages':[{}]}}})
    assert a['errors']['coverage_percent']==20.0 and a['errors']['pages']==1

def test_zip_version_and_normalization():
    inv={'drug':'test','evidence':{},'generated_utc':'2026-10-27'}
    graph=nx.DiGraph()
    raw=complete_report_zip(inv,graph,'test')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert 'normalization_review.json' in z.namelist()
        manifest=json.loads(z.read('manifest.json'))
        assert manifest['application_version']=='1.0.11.1-testing'
