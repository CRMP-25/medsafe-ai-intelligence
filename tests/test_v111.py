import ast
from pathlib import Path
from semantic_v106 import semantic_graph
from reporting_v107 import complete_report_zip
import json,io,zipfile

def test_semantic_graph_no_500_record_truncation():
    rows=[{'safetyreportid':str(i),'patient':{'reaction':[{'reactionmeddrapt':'TEST EVENT'}]}} for i in range(650)]
    inv={'drug':'example','evidence':{'errors':{'results':rows}}}
    g=semantic_graph(inv)
    assert sum(d.get('kind')=='record' for _,d in g.nodes(data=True))==650
    with zipfile.ZipFile(io.BytesIO(complete_report_zip(inv,g,'example'))) as z:
        manifest=json.loads(z.read('manifest.json'))
        assert manifest['application_version']=='1.0.11-testing'
        assert manifest['record_sources']['errors']==650

def test_one_zip_on_main_not_graph():
    text=Path(__file__).resolve().parents[1].joinpath('app.py').read_text()
    ast.parse(text)
    main=text.split('with t0:',1)[1].split('with t1:',1)[0]
    graph=text.split('with t5:',1)[1]
    assert main.count('Download Complete Investigation Outputs (ZIP)')==1
    assert 'complete_report_zip(' not in graph
    assert 'semantic_graph(current, limit_per_kind=None)' in main
    assert 'complete_v111.zip' in main
