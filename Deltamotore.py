from utils import funzionidb as fdb
import streamlit as st
import pandas as pd

# impostazioni streamlit
st.set_page_config(layout="wide")
st.title('Delta BOM motore')
st.divider()
# importazione file

up_sap = fdb.carica_excel_side('Caricare  D33')
up_plm = fdb.carica_excel_side('Caricare ZD33')

raw_sap = fdb.sap_raw(up_sap)
raw_plm = fdb.plm_raw(up_plm)


if st.toggle('Abilita filtro flag'):
# da qui viene applicato il filtro sulla merce sfusa
    SAP_BOM = fdb.elabora_sap(raw_sap, lay = 'no_flag')
    PLM_BOM = fdb.elabora_plm (raw_plm, lay = 'no_flag')
else:
    SAP_BOM = fdb.elabora_sap_nofiltro(raw_sap, lay = 'no_flag')
    PLM_BOM = fdb.elabora_plm_nofiltro (raw_plm, lay = 'no_flag')


motore_plm = fdb.isola_motore(PLM_BOM)

# split delle distinte
sap_struttura = fdb.isola_strutture(SAP_BOM)[0]
sap_no_figli = fdb.isola_strutture(SAP_BOM)[1]

plm_struttura = fdb.isola_strutture(motore_plm)[0]
plm_no_figli = fdb.isola_strutture(motore_plm)[1]

# plot -----------

st.subheader('Confronto livelli 3 senza figli',divider = 'red')
conf = fdb.confronta_no_figli(sap_no_figli,plm_no_figli)[0]
st.dataframe(conf, width=1500)
st.write('Codici senza figli: ',fdb.confronta_no_figli(sap_no_figli,plm_no_figli)[1])
st.write('Codici senza figli ok: ',fdb.confronta_no_figli(sap_no_figli,plm_no_figli)[1] - fdb.confronta_no_figli(sap_no_figli,plm_no_figli)[2])

st.subheader('Visualizzazione strutture appaiate',divider = 'red')
fdb.visualizza_appaiato(sap_struttura, plm_struttura)
