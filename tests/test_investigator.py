from investigator import annual_trend, classify_reactions, evidence_gate, investigation_report

def test_trend():
    assert annual_trend([{'time':'20260101','count':2},{'time':'20261201','count':3},{'time':'bad','count':4}]) == [{'year':'2026','report_count':5}]

def test_classification():
    assert 'Dosing / overdose' in classify_reactions({'patient':{'reaction':[{'reactionmeddrapt':'Accidental overdose'}]}})

def test_gates():
    gate=evidence_gate({'events':{'url':'https://api.fda.gov/test','results':[]}})
    assert gate['sources']['events']=='AVAILABLE'
    assert gate['sources']['labels']=='UNAVAILABLE'
    assert gate['clinical_recommendation']=='BLOCKED'

def test_report_escapes():
    page=investigation_report({'drug':'<script>','evidence':{},'generated_utc':'now'})
    assert '<h1>MedSafe | <script>' not in page and '&lt;script&gt;' in page.lower()
