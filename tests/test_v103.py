from unittest.mock import patch
import core

def test_paginated_totals_and_urls():
    def fake(endpoint, params):
        skip=params['skip']
        return {'results':[{'safetyreportid':str(i)} for i in range(skip, min(skip+params['limit'],5))],
                'total':5,'url':f'https://example.org/?skip={skip}','retrieved_utc':'2026-10-26T00:00:00Z'}
    with patch.object(core,'fetch',side_effect=fake):
        result=core.paginated_fetch('drug/event','example',max_records=10,page_size=2)
    assert result['retrieved']==5 and result['total']==5 and result['complete']
    assert len(result['pages'])==3

def test_paginated_cap_disclosed():
    def fake(endpoint,params):
        return {'results':[{'id':i} for i in range(params['limit'])], 'total':900,
                'url':'https://example.org','retrieved_utc':'now'}
    with patch.object(core,'fetch',side_effect=fake):
        result=core.paginated_fetch('drug/event','example',max_records=4,page_size=2)
    assert result['retrieved']==4 and result['truncated'] and not result['complete']

def test_report_version_deduplication():
    records=[{'safetyreportid':'A','safetyreportversion':'1'},
             {'safetyreportid':'A','safetyreportversion':'2'},
             {'safetyreportid':'B'}]
    unique=core.unique_case_rows(records)
    assert len(unique)==2
    assert unique[0]['safetyreportversion']=='2'
