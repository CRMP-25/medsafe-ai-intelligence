"""Evidence-gated, deterministic safety investigation helpers. No LLM dependency."""
from datetime import datetime, timezone
import html, json, re

ERROR_TERMS = {
    'Dosing / overdose': ('overdose', 'incorrect dose', 'wrong dose', 'dose omission', 'underdose'),
    'Administration': ('incorrect route', 'wrong route', 'administration error', 'incorrect administration'),
    'Product confusion': ('drug name confusion', 'product confusion', 'wrong drug', 'wrong product'),
    'Medication error (general)': ('medication error', 'drug dispensing error', 'prescribing error'),
}

def classify_reactions(report):
    terms = [r.get('reactionmeddrapt','') for r in report.get('patient',{}).get('reaction',[]) if isinstance(r,dict)]
    return sorted({category for category, patterns in ERROR_TERMS.items() if any(p in term.casefold() for term in terms for p in patterns)})

def annual_trend(rows):
    """Aggregate counts returned by openFDA count=receivedate; not patient incidence."""
    years={}
    for row in rows:
        term=str(row.get('time',row.get('term','')))
        if re.fullmatch(r'\d{8}',term):
            year=term[:4]
            years[year]=years.get(year,0)+int(row.get('count',0))
    return [{'year':year,'report_count':years[year]} for year in sorted(years)]

def evidence_gate(evidence):
    status={key:('AVAILABLE' if isinstance(evidence.get(key),dict) and not evidence[key].get('error') and evidence[key].get('url') else 'UNAVAILABLE') for key in ('events','errors','labels','recalls')}
    return {'sources':status,'causality':'NOT_ESTABLISHED','incidence':'NOT_ESTABLISHED','comparative_safety':'NOT_ESTABLISHED','clinical_recommendation':'BLOCKED','interpretation':'Retrieved reports and regulatory records support evidence exploration, not causal or comparative risk claims.'}

def investigation_report(inv):
    drug=html.escape(inv['drug']); gate=evidence_gate(inv.get('evidence',{}))
    sections=[f'<h1>MedSafe | {drug.title()} safety investigation</h1>',f'<p>Generated UTC: {html.escape(inv.get("generated_utc",""))}</p>', '<p><strong>Research demonstration — not clinical decision support.</strong></p>', '<h2>Evidence gates</h2><ul>']
    sections += [f'<li>{html.escape(k)}: {html.escape(v)}</li>' for k,v in gate['sources'].items()]
    sections += ['</ul><p>FAERS reports cannot establish incidence, causation, or comparative safety.</p>','<h2>Source-level provenance</h2><ul>']
    for kind, payload in inv.get('evidence',{}).items():
        url=payload.get('url') if isinstance(payload,dict) else None
        sections.append(f'<li>{html.escape(kind)}: '+(f'<a href="{html.escape(url,quote=True)}">{html.escape(url)}</a>' if url else 'Unavailable')+'</li>')
    sections += ['</ul><h2>Retrieved evidence summary</h2><ul>']
    for kind, payload in inv.get('evidence',{}).items():
        count=len(payload.get('results',[])) if isinstance(payload,dict) else 0
        sections.append(f'<li>{html.escape(kind)}: {count} retrieved records or aggregates (API limits apply)</li>')
    sections.append('</ul>')
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>MedSafe Investigation</title><style>body{font:16px system-ui;max-width:850px;margin:48px auto;line-height:1.55;color:#183049}h1,h2{color:#075e75}li{margin:8px 0;overflow-wrap:anywhere}</style></head><body>'+''.join(sections)+'</body></html>'
