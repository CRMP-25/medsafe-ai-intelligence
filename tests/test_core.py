from core import disproportionality,graph
import pytest
def test_ror():
    x=disproportionality(20,80,10,90)
    assert x['ROR']==2.25
    assert x['ROR_CI95_low']<2.25<x['ROR_CI95_high']
def test_zero():
    assert disproportionality(0,1,2,3)['haldane_correction']
def test_bad():
    with pytest.raises(ValueError):disproportionality(-1,2,3,4)
def test_graph():
    g=graph('naloxone',[{'term':'Headache','count':3}],['warnings'])
    assert g.has_edge('naloxone','Headache')

def test_annual_totals(monkeypatch):
    import core
    def fake(endpoint, params):
        year=params['search'].split('receivedate:[')[1][:4]
        return {'total':int(year),'url':'https://api.fda.gov/test','retrieved_utc':'now','results':[]}
    monkeypatch.setattr(core,'fetch',fake)
    x=core.annual_report_totals('naloxone',2024,2025)
    assert [r['report_count'] for r in x['results']]==[2024,2025]
    assert not x['failures']

def test_invalid_zero_margins():
    with pytest.raises(ValueError): disproportionality(0,0,1,1)
