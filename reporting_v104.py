"""Evidence-linked, deterministic exports and graph views for MedSafe V1.0.4."""
import json
import re
import networkx as nx
from urllib.parse import quote

KINDS=('events','errors','labels','recalls')

def clean(value, limit=240):
    return re.sub(r'\s+',' ',str(value or '')).strip()[:limit]

def record_link(kind, row, fallback):
    if kind=='errors' and row.get('safetyreportid'):
        return 'https://api.fda.gov/drug/event.json?search='+quote('safetyreportid:"'+str(row['safetyreportid'])+'"')+'&limit=1'
    if kind=='labels' and row.get('id'):
        return 'https://api.fda.gov/drug/label.json?search='+quote('id:"'+str(row['id'])+'"')+'&limit=1'
    if kind=='recalls' and row.get('recall_number'):
        return 'https://api.fda.gov/drug/enforcement.json?search='+quote('recall_number:"'+str(row['recall_number'])+'"')+'&limit=1'
    return fallback or ''

def summary(kind,row):
    if kind=='errors':
        terms=[clean(x.get('reactionmeddrapt')) for x in row.get('patient',{}).get('reaction',[]) if isinstance(x,dict)]
        return f"Report {clean(row.get('safetyreportid'))}; received {clean(row.get('receivedate'))}; reactions: {', '.join(terms[:8]) or 'not provided'}"
    if kind=='labels':
        of=row.get('openfda') or {}; names=of.get('brand_name') or of.get('generic_name') or []
        sections=[k.replace('_',' ') for k in ('boxed_warning','warnings','contraindications') if row.get(k)]
        return f"{clean(', '.join(names) or row.get('id'))}; sections: {', '.join(sections) or 'not captured'}"
    if kind=='recalls':
        return f"Recall {clean(row.get('recall_number'))}; {clean(row.get('status'))}; {clean(row.get('report_date'))}; reason: {clean(row.get('reason_for_recall'))}"
    return f"{clean(row.get('term'))}: {row.get('count','unknown')} reports (aggregate)"

def markdown_report(inv):
    drug=clean(inv.get('drug')); evidence=inv.get('evidence') or {}
    out=[f'# MedSafe AI Intelligence | {drug.title()} evidence investigation','',f"Generated UTC: {clean(inv.get('generated_utc'))}",'',
         '> Research and educational evidence exploration only. FAERS spontaneous reports do not establish causality, incidence, comparative risk, or clinical recommendations.','',
         '## Retrieval completeness','', '| Evidence | Retrieved | Matching (API) | Coverage |','|---|---:|---:|---:|']
    for kind in KINDS:
        data=evidence.get(kind) or {}; n=len(data.get('results') or []); total=data.get('total')
        coverage=f'{100*n/total:.1f}%' if isinstance(total,int) and total>0 else 'Unknown'
        out.append(f'| {kind} | {n:,} | {total:,} | {coverage} |' if isinstance(total,int) else f'| {kind} | {n:,} | Unknown | {coverage} |')
    out+=['','Counts describe retrieved reports or records, not patients or clinical incidence. Matching totals depend on the exact API queries and may change.','',
          '## Evidence sources and retrieval provenance','']
    for kind in KINDS:
        data=evidence.get(kind) or {}; out.append(f'### {kind.title()}')
        out.append(f'- Query: {data.get("query") or "see URL"}')
        out.append(f'- Retrieved UTC: {clean(data.get("retrieved_utc"))}')
        if data.get('url'):out.append(f'- [openFDA source query]({data["url"]})')
        if data.get('error'):out.append(f'- **Retrieval error:** {clean(data["error"])}')
        for i,page in enumerate(data.get('pages') or [],1):
            if page.get('url'):out.append(f'- [Page {i}: {page.get("count",0)} records]({page["url"]}) — {clean(page.get("retrieved_utc"))}')
        out.append('')
    out+=['## Retrieved record summaries','', 'The following lists **every retrieved record or aggregate** in this investigation. Each link points to a record-specific openFDA query when an identifier is available; otherwise it points to the original query. These are summaries, not complete raw JSON.','']
    for kind in KINDS:
        data=evidence.get(kind) or {}; out.append(f'### {kind.title()} ({len(data.get("results") or []):,} retrieved)')
        for i,row in enumerate(data.get('results') or [],1):
            if not isinstance(row,dict):continue
            description=summary(kind,row).replace('[','\\[').replace(']','\\]')
            link=record_link(kind,row,data.get('url'))
            out.append(f'{i}. {description}'+(f' — [FDA source]({link})' if link else ''))
        if not data.get('results'):out.append('No records retrieved.')
        out.append('')
    out+=['## Evidence interpretation and limitations','',
          '- FAERS signals reflect reports, not established adverse drug reactions or causality.',
          '- Search terms are non-exhaustive; some matches may be duplicates, historical versions, or misclassified.',
          '- Label records may represent different products, formulations, manufacturers, or revisions.',
          '- Recall statuses must be checked against current FDA records; historical recalls are not necessarily active.',
          '- Graph edges denote query provenance, document membership, or reported associations, not clinical mechanisms.',
          '- The JSON investigation export preserves retrieved payloads and should accompany this human-readable summary.','']
    return '\n'.join(out)

def build_evidence_graph(inv, selected=('events','errors','labels','recalls'), max_per_kind=12):
    """Hierarchical evidence graph; typed, non-causal relationships only."""
    drug=str(inv.get('drug','medication')); evidence=inv.get('evidence') or {}
    g=nx.DiGraph(); g.add_node(drug,kind='medication',label=drug)
    for kind in KINDS:
        if kind not in selected:continue
        payload=evidence.get(kind) or {}; records=payload.get('results') or []
        category=f'Category: {kind}'; g.add_node(category,kind='category',label=kind.title(),count=len(records))
        g.add_edge(drug,category,relation='evidence category',source=payload.get('url') or '')
        for index,row in enumerate(records[:max_per_kind]):
            if not isinstance(row,dict):continue
            identifier=(row.get('safetyreportid') if kind=='errors' else row.get('id') if kind=='labels' else row.get('recall_number') if kind=='recalls' else row.get('term')) or str(index)
            node=f'{kind}:{identifier}'
            g.add_node(node,kind='record',category=kind,label=clean(identifier,40),summary=summary(kind,row),url=record_link(kind,row,payload.get('url')))
            g.add_edge(category,node,relation='retrieved record' if kind!='events' else 'reported term aggregate',source=payload.get('url') or '')
    return g

def graphml_bytes(g):
    return '\n'.join(nx.generate_graphml(g)).encode('utf-8')
