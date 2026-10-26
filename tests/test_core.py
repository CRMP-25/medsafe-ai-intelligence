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
