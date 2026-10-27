import io,zipfile,csv
import networkx as nx
from semantic_v106 import associations
from reporting_v107 import complete_report_zip

def test_all_provenance_exported():
    g=nx.DiGraph()
    g.add_node('a',kind='adverse_event',label='A');g.add_node('b',kind='adverse_event',label='B')
    for i in range(12):
        r=f'r{i}';g.add_node(r,kind='record',source_kind='errors',source_id=str(i),source_url=f'https://example.org/{i}')
        g.add_edge(r,'a');g.add_edge(r,'b')
    pair=associations(g)[0]
    assert pair['co_reported_records']==12
    assert len(pair['source_ids'].split(', '))==12
    assert len(pair['source_urls'].split(' | '))==12
    blob=complete_report_zip({'drug':'test','evidence':{}},g,'test')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        assert len(z.namelist())==10
        rows=list(csv.DictReader(io.StringIO(z.read('associations.csv').decode())))
        assert len(rows[0]['source_ids'].split(', '))==12
