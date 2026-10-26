import io,json,zipfile
import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
from core import *
from investigator import annual_trend, classify_reactions, evidence_gate, investigation_report
st.set_page_config(page_title='MedSafe AI Intelligence',page_icon='🛡️',layout='wide')
st.markdown('''<style>.block-container{padding-top:1.3rem}.hero{background:linear-gradient(110deg,#12233e,#126b83);padding:24px;border-radius:16px;color:white}.hero h1{color:white;margin:0}.hero p{color:#d7f5fa;margin:8px 0 0}</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🛡️ MedSafe AI Intelligence · V1.0.2-testing</h1><p>Medication Safety & Substance Use Care | Evidence-grounded conference demonstration · October 30, 2026</p></div>',unsafe_allow_html=True)
st.warning('FAERS is a spontaneous reporting system: reports do not establish causality, incidence, comparative safety, or a population risk denominator. Duplicate and incomplete reports are possible. Educational research tool; not clinical decision support.')
drug=st.sidebar.selectbox('Medication',DRUGS)
st.sidebar.caption('Live openFDA requests; source timestamps and URLs retained in investigation exports.')
@st.cache_data(ttl=1800,show_spinner=False)
def load(kind,drug): return {'events':events,'trend':trend,'labels':labels,'recalls':recalls,'errors':errors}[kind](drug)
def safe(kind):
    try:return load(kind,drug)
    except Exception as e:st.error(f'{kind} unavailable: {e}');return None
def table(data):
    return pd.DataFrame([{'term':r.get('term',''),'count':r.get('count',0)} for r in data.get('results',[])])
t1,t2,t3,t4=st.tabs(['📊 Safety Signal Explorer','⚠️ Medication Error Intelligence','📜 Regulatory Evidence','🧠 Agentic Safety Investigator'])
with t1:
    st.subheader('FAERS reported adverse-event terms')
    ev=safe('events')
    if ev:
        df=table(ev)
        if not df.empty:st.plotly_chart(px.bar(df.head(15),x='count',y='term',orientation='h',title='Reported terms (not unique patients)').update_layout(yaxis={'categoryorder':'total ascending'}),use_container_width=True)
        st.caption('Source: '+ev['url'])
    st.markdown('#### Reporting trend by received year')
    tr=safe('trend')
    if tr:
        yearly=[r for r in tr.get('results',[]) if isinstance(r.get('report_count'),int)]
        if yearly: st.plotly_chart(px.line(pd.DataFrame(yearly),x='year',y='report_count',markers=True,title='FAERS reports by receipt year (not incidence)'),use_container_width=True)
        else: st.info('No annual totals were available from openFDA.')
        if tr.get('failures'): st.warning(f"{len(tr['failures'])} year(s) unavailable from openFDA; missing years are not zero.")
        with st.expander('Annual trend source URLs and retrieval status'):
            st.dataframe(pd.DataFrame(tr.get('results',[])),use_container_width=True)
            if tr.get('failures'): st.json(tr['failures'])
        st.caption('Annual bounded FAERS report queries (meta.results.total); not incidence. Individual source URLs and timestamps above. Results may change with FAERS updates.')
    st.markdown('#### Disproportionality calculator · explicit 2 × 2 table')
    st.caption('a=drug+event, b=drug+other events, c=other drugs+event, d=other drugs+other events. Supply deduplicated, consistently defined FAERS case counts. The counts charted above cannot supply this table.')
    cols=st.columns(4); vals=[cols[i].number_input(k,min_value=0,value=v,step=1) for i,(k,v) in enumerate(zip(['a','b','c','d'],[30,170,60,740]))]
    st.info('Illustrative values prefilled below are SYNTHETIC, not retrieved from FAERS. Do not cite them as a measured signal.')
    if st.button('Calculate ROR / PRR'):
        try:st.json(disproportionality(*map(int,vals)))
        except Exception as e:st.error(str(e))
    st.caption('ROR 95% CI uses the large-sample log-Wald approximation; zero cells receive a 0.5 continuity correction. PRR is descriptive; neither statistic is a causal effect.')
with t2:
    st.subheader('Medication error reports')
    st.caption('Selected MedDRA terms are grouped into dosing, administration, product confusion and general error categories. This is a non-exhaustive term-based screen, not validated case adjudication.')
    er=safe('errors')
    if er:
        rows=[]
        for r in er['results']:
            rows.append({'safetyreportid':r.get('safetyreportid'),'receivedate':r.get('receivedate'),'categories':', '.join(classify_reactions(r)) or 'Unclassified', 'reactions':'; '.join(x.get('reactionmeddrapt','') for x in r.get('patient',{}).get('reaction',[]))})
        if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True)
        else: st.info('No matching medication-error reports returned for this query.')
        st.caption('Source: '+er['url'])
with t3:
    st.subheader('FDA labeling and recall records')
    lab=safe('labels'); rec=safe('recalls')
    if lab:
        for i,r in enumerate(lab['results']):
            with st.expander(f"Label {i+1} · {', '.join(r.get('openfda',{}).get('brand_name',[])[:2]) or drug}"):
                for k in ['boxed_warning','warnings','contraindications','precautions','dosage_and_administration']:
                    if r.get(k):st.markdown('**'+k.replace('_',' ').title()+'**');st.write(' '.join(r[k])[:7000])
        st.caption('Label query: '+lab['url'])
    if rec:
        recall_rows=[{'date':x.get('report_date'),'reason':x.get('reason_for_recall'),'status':x.get('status'),'recall_number':x.get('recall_number')} for x in rec['results']]
        if recall_rows: st.dataframe(pd.DataFrame(recall_rows),use_container_width=True)
        else: st.info('No matching recall records returned for this query.')
        st.caption('Recall query: '+rec['url'])
with t4:
    st.subheader('Reproducible evidence investigation · no LLM required')
    st.caption('Deterministic evidence retrieval and graph construction. Graph edges denote database co-reporting or document membership, not proven clinical mechanisms.')
    if st.button('Run investigation',type='primary'):
        evidence={}
        for kind in ['events','errors','labels','recalls']:
            try:evidence[kind]=load(kind,drug)
            except Exception as e:evidence[kind]={'error':str(e),'results':[]}
        st.session_state['investigation']={'drug':drug,'generated_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'evidence':evidence,'limitations':['Spontaneous reports cannot establish causality or incidence.','Term searches may miss synonyms, coding variants, and duplicate records.','Graph connections are evidence associations, not causal edges.']}
    inv=st.session_state.get('investigation')
    if inv and inv['drug']==drug:
        evidence=inv['evidence']; reactions=evidence['events'].get('results',[])[:12]
        sections=[x for x in ['boxed_warning','warnings','contraindications'] if any(x in z for z in evidence['labels'].get('results',[]))]
        g=graph(drug,reactions,sections)
        import plotly.graph_objects as go
        pos=nx.spring_layout(g,seed=17)
        edges=[]
        for u,v in g.edges():edges.append(go.Scatter(x=[pos[u][0],pos[v][0],None],y=[pos[u][1],pos[v][1],None],mode='lines',line={'color':'#91a7bb'},hoverinfo='skip',showlegend=False))
        nodes=go.Scatter(x=[pos[n][0] for n in g],y=[pos[n][1] for n in g],text=list(g.nodes),mode='markers+text',textposition='top center',marker={'size':[24 if n==drug else 13 for n in g],'color':['#087e8b' if n==drug else '#e3a548' for n in g]},hovertext=[str(g.nodes[n]) for n in g],hoverinfo='text',showlegend=False)
        st.plotly_chart(go.Figure(data=edges+[nodes],layout={'height':540,'xaxis':{'visible':False},'yaxis':{'visible':False},'margin':{'l':10,'r':10,'t':20,'b':10}}),use_container_width=True)
        st.markdown('**Evidence gates:**')
        st.json(evidence_gate(evidence))
        st.markdown('**Evidence-grounded findings:**')
        st.write(f"For {drug}, the current retrieval returned {len(reactions)} displayed reaction terms, {len(evidence['errors'].get('results',[]))} medication-error matching records, {len(evidence['labels'].get('results',[]))} label records, and {len(evidence['recalls'].get('results',[]))} recall records. These are retrieval counts, not incidence or risk estimates.")
        report=json.dumps(inv,indent=2,default=str)
        st.download_button('Download investigation JSON + provenance',report,file_name=f'medsafe_{drug}_investigation.json',mime='application/json')
        st.download_button('Download knowledge graph GraphML', '\n'.join(nx.generate_graphml(g)),file_name=f'medsafe_{drug}_graph.graphml',mime='application/xml')

        st.download_button('Download printable HTML investigation report',investigation_report(inv),file_name=f'medsafe_{drug}_report.html',mime='text/html')
