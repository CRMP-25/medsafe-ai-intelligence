import io,json,zipfile
import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
from core import *
from investigator import annual_trend, classify_reactions, evidence_gate, investigation_report
from reporting_v104 import markdown_report, build_evidence_graph, graphml_bytes, summary, record_link
st.set_page_config(page_title='MedSafe AI Intelligence',page_icon='🛡️',layout='wide')
st.markdown('''<style>.block-container{padding-top:1.3rem}.hero{background:linear-gradient(110deg,#12233e,#126b83);padding:24px;border-radius:16px;color:white}.hero h1{color:white;margin:0}.hero p{color:#d7f5fa;margin:8px 0 0}</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🛡️ MedSafe AI Intelligence · V1.0.4.1-testing</h1><p>Medication Safety & Substance Use Care | Evidence-grounded conference demonstration · October 30, 2026</p></div>',unsafe_allow_html=True)
st.warning('FAERS is a spontaneous reporting system: reports do not establish causality, incidence, comparative safety, or a population risk denominator. Duplicate and incomplete reports are possible. Educational research tool; not clinical decision support.')
drug=st.sidebar.selectbox('Medication',DRUGS)
st.sidebar.caption('Live openFDA requests; source timestamps and URLs retained in investigation exports.')
@st.cache_data(ttl=1800,show_spinner=False)
def load(kind,drug): return {'events':events,'trend':trend,'labels':labels,'recalls':recalls,'errors':errors}[kind](drug)
def safe(kind):
    try:return load(kind,drug)
    except Exception as e:st.error(f'{kind} unavailable: {e}');return None
def coverage(data, label):
    if not data:return
    total=data.get('total'); retrieved=len(data.get('results',[]))
    if total is not None:
        st.metric(f'{label}: retrieved / total matching',f'{retrieved:,} / {total:,}')
        if retrieved<total:st.warning(f'Partial retrieval: {retrieved:,} of {total:,} matching records. This is not a complete population.')
    else:st.caption(f'{label}: {retrieved:,} retrieved; provider total not available.')
    if data.get('error'):st.error('Retrieval stopped early: '+str(data['error']))
    if data.get('pages'):
        with st.expander(f'{label} · API page provenance'):
            st.dataframe(pd.DataFrame(data['pages']),use_container_width=True)
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
        coverage(er,'Medication-error reports')
        deduped=unique_case_rows(er['results'])
        st.caption(f'Unique safetyreportid records in retrieved pages: {len(deduped):,}; raw retrieved: {len(er["results"]):,}. This is report-ID deduplication, not validated clinical case adjudication.')
        rows=[]
        for r in deduped:
            rows.append({'safetyreportid':r.get('safetyreportid'),'receivedate':r.get('receivedate'),'version':r.get('safetyreportversion'),'categories':', '.join(classify_reactions(r)) or 'Unclassified', 'reactions':'; '.join(x.get('reactionmeddrapt','') for x in r.get('patient',{}).get('reaction',[]))})
        if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True)
        else: st.info('No matching medication-error reports returned for this query.')
        st.caption('Source: '+str(er.get('url') or 'unavailable'))
with t3:
    st.subheader('FDA labeling and recall records')
    lab=safe('labels'); rec=safe('recalls')
    if lab:
        coverage(lab,'FDA labels')
        label_rows=[]
        for i,r in enumerate(lab['results']):
            of=r.get('openfda') or {}
            label_rows.append({'number':i+1,'product':', '.join(of.get('brand_name') or of.get('generic_name') or []) or drug,
                               'label_id':r.get('id',''), 'boxed_warning':bool(r.get('boxed_warning')),
                               'warnings':bool(r.get('warnings')), 'contraindications':bool(r.get('contraindications'))})
        if label_rows:
            label_df=pd.DataFrame(label_rows)
            search_label=st.text_input('Search labels by product name or label ID',key='label_search_v104')
            if search_label:
                mask=label_df[['product','label_id']].astype(str).apply(lambda col:col.str.contains(search_label,case=False,regex=False)).any(axis=1)
                label_df=label_df[mask]
            only_boxed=st.checkbox('Show only labels with boxed warnings',key='label_boxed_v104')
            if only_boxed:label_df=label_df[label_df['boxed_warning']]
            st.dataframe(label_df,use_container_width=True,hide_index=True)
            if not label_df.empty:
                choice=st.selectbox('Inspect a label',label_df['number'].tolist(),format_func=lambda n:f'Label {n}: {label_rows[n-1]["product"]} ({str(label_rows[n-1]["label_id"])[:12]})')
                selected_label=lab['results'][choice-1]
                for k in ['boxed_warning','warnings','contraindications','precautions','dosage_and_administration']:
                    if selected_label.get(k):
                        with st.expander(k.replace('_',' ').title(),expanded=(k=='boxed_warning')):
                            st.write(' '.join(selected_label[k])[:12000])
                st.markdown(f'[Open FDA source for this label]({record_link("labels",selected_label,lab.get("url"))})')
            else:st.info('No labels match the selected filters.')
        st.caption('Label query: '+lab['url'])
    if rec:
        coverage(rec,'FDA recalls')
        recall_rows=[{'date':pd.to_datetime(x.get('report_date'),format='%Y%m%d',errors='coerce').date() if x.get('report_date') else None,'reason':x.get('reason_for_recall'),'status':x.get('status'),'recall_number':x.get('recall_number')} for x in rec['results']]
        if recall_rows:
            rdf=pd.DataFrame(recall_rows)
            statuses=['All']+sorted(str(x) for x in rdf['status'].dropna().unique())
            chosen=st.selectbox('Recall status',statuses)
            if chosen!='All':rdf=rdf[rdf['status']==chosen]
            st.dataframe(rdf,use_container_width=True)
        else: st.info('No matching recall records returned for this query.')
        st.caption('Recall query: '+rec['url'])

def render_investigation_graph(inv, selected_kinds, max_nodes):
    import plotly.graph_objects as go
    drug=inv["drug"]
    g=build_evidence_graph(inv,selected_kinds,max_nodes)
    # Hierarchical layout: medication -> evidence category -> retrieved record.
    categories=[n for n,d in g.nodes(data=True) if d.get('kind')=='category']
    pos={drug:(0,0)}
    for i,category in enumerate(categories):
        y=(len(categories)-1)/2-i
        pos[category]=(1.5,y*2.4)
        children=list(g.successors(category))
        for j,node in enumerate(children):pos[node]=(3.4,y*2.4+(j-(len(children)-1)/2)*0.24)
    edge_x=[];edge_y=[]
    for u,v in g.edges():
        if u in pos and v in pos:edge_x += [pos[u][0],pos[v][0],None];edge_y += [pos[u][1],pos[v][1],None]
    edge_trace=go.Scatter(x=edge_x,y=edge_y,mode='lines',line={'color':'#8194a8','width':1},hoverinfo='skip',showlegend=False)
    traces=[edge_trace]
    for kind,colour,size in [('medication','#0d9fa5',24),('category','#f3b14b',17),('record','#88b9df',9)]:
        nodes=[n for n,d in g.nodes(data=True) if d.get('kind')==kind and n in pos]
        traces.append(go.Scatter(x=[pos[n][0] for n in nodes],y=[pos[n][1] for n in nodes],mode='markers+text' if kind!='record' else 'markers',
            text=[g.nodes[n].get('label',n) for n in nodes],textposition='top center',
            hovertext=[g.nodes[n].get('summary',g.nodes[n].get('label',n)) for n in nodes],hoverinfo='text',
            marker={'size':size,'color':colour},name=kind))
    st.plotly_chart(go.Figure(data=traces,layout={'height':620,'xaxis':{'visible':False},'yaxis':{'visible':False},'margin':{'l':20,'r':20,'t':20,'b':20},'hovermode':'closest'}),use_container_width=True)
    record_nodes=[n for n,d in g.nodes(data=True) if d.get('kind')=='record']
    if record_nodes:
        chosen_node=st.selectbox('Inspect evidence node',record_nodes,format_func=lambda n:f'{g.nodes[n].get("category", "")}: {g.nodes[n].get("label",n)}')
        node=g.nodes[chosen_node]
        st.write(node.get('summary',''))
        if node.get('url'):st.markdown(f'[Open corresponding FDA record query]({node["url"]})')
    return g

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
        # Exports are independent of the optional visualization.
        st.markdown('#### Investigation evidence exports')
        st.download_button('Download comprehensive Markdown evidence report',markdown_report(inv),file_name=f'medsafe_{drug}_evidence.md',mime='text/markdown',key='md_v1041')
        st.download_button('Download investigation JSON + provenance',json.dumps(inv,indent=2,default=str),file_name=f'medsafe_{drug}_investigation.json',mime='application/json',key='json_v1041')
        st.download_button('Download printable HTML investigation report',investigation_report(inv),file_name=f'medsafe_{drug}_report.html',mime='text/html',key='html_v1041')
        st.markdown('#### Explore evidence-linked knowledge graph')
        st.caption('Change settings, then select Apply Graph Settings. Changing controls alone does not rebuild the graph.')
        graph_key='graph_applied_v1041'
        if st.session_state.get(graph_key,{}).get('drug')!=drug:
            st.session_state[graph_key]={'drug':drug,'layers':['events','errors','labels','recalls'],'nodes':8}
        with st.form('graph_settings_form_v1041'):
            selected_kinds=st.multiselect('Evidence layers',['events','errors','labels','recalls'],default=st.session_state[graph_key]['layers'])
            max_nodes=st.slider('Records per evidence layer',min_value=3,max_value=15,value=st.session_state[graph_key]['nodes'],step=1)
            apply_settings=st.form_submit_button('Apply Graph Settings')
        if apply_settings:
            st.session_state[graph_key]={'drug':drug,'layers':selected_kinds,'nodes':max_nodes}
        applied=st.session_state[graph_key]
        st.caption(f"Graph settings applied: {applied['nodes']} records per layer; {len(applied['layers'])} selected layers. Maximum 15 per layer.")
        try:
            g=render_investigation_graph(inv,applied['layers'],applied['nodes'])
            st.download_button('Download knowledge graph GraphML',graphml_bytes(g),file_name=f'medsafe_{drug}_graph.graphml',mime='application/xml',key='graphml_v1041')
            st.caption('Showing a bounded, filterable subset of retrieved evidence nodes. Graph edges indicate record membership or reported terms, not proven causality.')
        except Exception as graph_exc:
            st.error('The graph could not be rendered. Investigation findings and report downloads remain available above.')
            st.caption(f'Graph diagnostic: {type(graph_exc).__name__}: {str(graph_exc)[:300]}')
        st.markdown('**Evidence gates:**')
        st.json(evidence_gate(evidence))
        st.markdown('**Evidence-grounded findings:**')
        st.write(f"For {drug}, the current retrieval returned {len(reactions)} displayed reaction terms, {len(evidence['errors'].get('results',[]))} medication-error records, {len(evidence['labels'].get('results',[]))} label records, and {len(evidence['recalls'].get('results',[]))} recall records. These are retrieval counts, not incidence or risk estimates.")
        for kind in ('errors','labels','recalls'):coverage(evidence[kind],kind.title())
