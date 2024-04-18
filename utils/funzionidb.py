import pandas as pd
import streamlit as st
import numpy as np

# definizione parametri
layout ={
    'standard':['Liv.','Articolo','Qty','MerceSfusa (BOM)','Ril.Tecn.','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Ril.Prod.','Ril.Ric.','Testo posizione riga 1',
    'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza'],

    'no_flag':['Liv.','Articolo','Qty','Testo breve oggetto','Gruppo Tecnico','Descr. Gruppo Tecnico','Testo posizione riga 1',
    'Testo posizione riga 2','STGR','Descrizione Sottogruppo','Gruppo appartenenza','Descr. Gruppo Appartenenza'],

    'bom_appaiate':['Articolo','Liv_PLM','descrizione_PLM','Qty PLM','Liv_SAP','descrizione_SAP','Qty SAP']
    
}

# funzioni-------------------------------------------------------------------------------

def sap_raw (df, lay='standard'):
    '''
    lay = 'standard' | 'sap_raw'

    azioni: rinomina colonne
    '''
    df['Liv.']=df['Liv. esplosione'].str.replace('.','')    
    df.rename(columns={'Materiale':'Articolo','Qtà comp. (UMC)':'Qty'},inplace=True)
    df = df[layout[lay]]
    return df

def plm_raw (df, lay='standard'):
    '''
    lay = 'standard' | 'sap_raw'
    azioni: rinomina colonne e trasforma i flag in True / False
    '''
    df['Liv.']=df['Liv. esplosione'].str.replace('.','')
    df.rename(columns={'Numero componenti':'Articolo','Qtà comp. (UMC)':'Qty','Merce sfusa':'MerceSfusa (BOM)','Ril. progettazione':'Ril.Tecn.','Rilevante produzione':'Ril.Prod.','Cd.parte di ricambio':'Ril.Ric.'},
            inplace=True)
    df['Liv.']= df['Liv.'].astype(int)
    df['MerceSfusa (BOM)']=df['MerceSfusa (BOM)'].apply(lambda x: 'Sì' if x == 'X' else 'No' )        
    df['Ril.Tecn.']=df['Ril.Tecn.'].apply(lambda x: True if x  =='X' else False)
    df['Ril.Prod.']=df['Ril.Prod.'].apply(lambda x: True if x  =='X' else False)
    df['Ril.Ric.']=df['Ril.Ric.'].apply(lambda x: True if x  =='X' else False)   
    df = df[layout[lay]]   
    return df

def carica_excel(testo):
    path = st.file_uploader(testo)
    if not path:
        st.stop()
    df = pd.read_excel(path)
    return df

def carica_excel_side(testo):
    path = st.sidebar.file_uploader(testo)
    if not path:
        st.stop()
    df = pd.read_excel(path)
    return df

def elabora_plm (df, lay='standard'): # in uso dopo introduzione analisi preliminare piattaforme

    #correzione gruppi teecnici mancanti
    for i in range(len(df)): 
        if (df['Liv.'].iloc[i] >2) and (df['Gruppo Tecnico'].astype(str).iloc[i]=='nan'):
            df['Gruppo Tecnico'].iloc[i] = df['Gruppo Tecnico'].iloc[i-1]
            df['Descr. Gruppo Tecnico'].iloc[i] = df['Descr. Gruppo Tecnico'].iloc[i-1]

    # step 1: eliminare tutti i figli con padre merce sfusa
    df['Eliminare'] = 0
    for i in range(len(df)):
        if i == len(df):
            break
        if (df.loc[i,'MerceSfusa (BOM)'] == 'Sì'):
            livello_padre = df.loc[i,'Liv.']
            df.loc[i,'Eliminare'] = 1
            j = i
            if (j+1) == len(df):
                break
            while df.loc[j+1,'Liv.']>livello_padre:
                df.loc[j+1,'Eliminare']=1
                j+=1
                if (j+1) == len(df):
                    break  

        if (df.loc[i,'MerceSfusa (BOM)'] == 'No') and (df.loc[i, 'Eliminare']==0):
            if ((df.loc[i,'Ril.Tecn.']==True) and (df.loc[i,'Ril.Prod.']==False) and (df.loc[i,'Ril.Ric.']==True)):                   
                df.loc[i,'Eliminare'] = 1
            else:
                df.loc[i,'Eliminare'] = 0
    # Filtro
    df = df.loc[df['Eliminare']==0] 
    df.reset_index(drop=True, inplace=True) 
    df = df[layout[lay]]
    return df

def elabora_sap (df, lay='standard'): # in uso dopo introduzione analisi preliminare piattaforme
    df['Liv.']= df['Liv.'].astype(int)
    
    # step 1: eliminare tutti i figli con padre livello 2 merce sfusa
    df['Eliminare'] = 0
    for i in range(len(df)):
        if i == len(df):
            break
        if (df.loc[i,'MerceSfusa (BOM)'] == 'Sì'): #and df.loc[i,'Liv.']== 2):
            df.loc[i,'Eliminare'] = 1
            livello_padre = df.loc[i,'Liv.']

            j = i
            if (j+1) == len(df):
                break
            while df.loc[j+1,'Liv.']>livello_padre:
                df.at[j+1,'Eliminare']=1
                j+=1
                if (j+1) == len(df):
                    break  
    # Filtro
    df = df.loc[df['Eliminare']==0] 
    
    df = df.drop(columns=['MerceSfusa (BOM)','Ril.Tecn.','Eliminare','Ril.Prod.','Ril.Ric.']) 
    df.reset_index(drop=True, inplace=True) 
    return df

def elabora_plm_nofiltro (df, lay='standard'): # in uso dopo introduzione analisi preliminare piattaforme

    #correzione gruppi teecnici mancanti
    for i in range(len(df)): 
        if (df['Liv.'].iloc[i] >2) and (df['Gruppo Tecnico'].astype(str).iloc[i]=='nan'):
            df['Gruppo Tecnico'].iloc[i] = df['Gruppo Tecnico'].iloc[i-1]
            df['Descr. Gruppo Tecnico'].iloc[i] = df['Descr. Gruppo Tecnico'].iloc[i-1]

    # step 1: eliminare tutti i figli con padre merce sfusa
    df['Eliminare'] = 0
    for i in range(len(df)):
        if i == len(df):
            break
        if (df.loc[i,'MerceSfusa (BOM)'] == 'Sì'):
            livello_padre = df.loc[i,'Liv.']
            df.loc[i,'Eliminare'] = 1
            j = i
            if (j+1) == len(df):
                break
            while df.loc[j+1,'Liv.']>livello_padre:
                df.loc[j+1,'Eliminare']=1
                j+=1
                if (j+1) == len(df):
                    break  

        if (df.loc[i,'MerceSfusa (BOM)'] == 'No') and (df.loc[i, 'Eliminare']==0):
            if ((df.loc[i,'Ril.Tecn.']==True) and (df.loc[i,'Ril.Prod.']==False) and (df.loc[i,'Ril.Ric.']==True)):                   
                df.loc[i,'Eliminare'] = 1
            else:
                df.loc[i,'Eliminare'] = 0
    # Filtro
    #df = df.loc[df['Eliminare']==0] 
    df.reset_index(drop=True, inplace=True) 
    df = df[layout[lay]]
    return df

def elabora_sap_nofiltro (df, lay='standard'): # in uso dopo introduzione analisi preliminare piattaforme
    df['Liv.']= df['Liv.'].astype(int)
    
    # step 1: eliminare tutti i figli con padre livello 2 merce sfusa
    df['Eliminare'] = 0
    for i in range(len(df)):
        if i == len(df):
            break
        if (df.loc[i,'MerceSfusa (BOM)'] == 'Sì'): #and df.loc[i,'Liv.']== 2):
            df.loc[i,'Eliminare'] = 1
            livello_padre = df.loc[i,'Liv.']

            j = i
            if (j+1) == len(df):
                break
            while df.loc[j+1,'Liv.']>livello_padre:
                df.at[j+1,'Eliminare']=1
                j+=1
                if (j+1) == len(df):
                    break  
    # Filtro
    #df = df.loc[df['Eliminare']==0] 
    
    df = df.drop(columns=['MerceSfusa (BOM)','Ril.Tecn.','Eliminare','Ril.Prod.','Ril.Ric.']) 
    df.reset_index(drop=True, inplace=True) 
    return df

def isola_strutture(df):
    '''
    output = (df_struttura, df_no_figli)

    '''
    df['Struttura'] = None
    df['Liv.'] = df['Liv.'].astype(int)

    if df['Liv.'].iloc[-1] == 3:
        df['Struttura'] = 'no'
    else:
        df['Struttura'] = 'si'

    for i in range(len(df)-1):
        livello = df['Liv.'].iloc[i]
        if livello == 2: 
            df.Struttura.iloc[i] = 'no'
        elif (livello == 3) and (df['Liv.'].iloc[i+1]==3):
            df.Struttura.iloc[i] = 'no'
        else:
            df.Struttura.iloc[i] = 'si'

    df_struttura = df[df.Struttura.astype(str) == 'si']
    df_struttura = df_struttura.reset_index(drop=True)
    df_no_figli = df[df.Struttura.astype(str) == 'no']
    df_no_figli = df_no_figli[1:]
    df_no_figli = df_no_figli.reset_index(drop=True)

    return df_struttura, df_no_figli

def partizione (SKU,BOM):
    indice = BOM.index[BOM['Articolo'] == SKU].tolist()
    idx=indice[0]
    livello_SKU = BOM.iloc[idx,0]
    j=idx+1
    if j == len(BOM):
        indice_target = idx
        df = BOM.iloc[idx:indice_target+1,:]
    elif BOM.iloc[j,0] <= livello_SKU:  
        indice_target = j
        df = BOM.iloc[idx:indice_target,:]
    else:
        while BOM.iloc[j,0] > livello_SKU:  
            if (j+1) == len(BOM):
                indice_target = j+1
                df = BOM.iloc[idx:indice_target+1,:]
                break
            j+=1  
            indice_target = j
            df = BOM.iloc[idx:indice_target,:]
    return df

def isola_motore(PLM_BOM):
    indice_motore = 0
    for i in range (len (PLM_BOM)):
        if PLM_BOM.loc[i,'Articolo'].startswith('0029'):
            indice_motore = i
        
    if indice_motore >= 0:    # eliminazione righe e assegnazione gt
        codice_motore = PLM_BOM.loc[indice_motore,'Articolo']
        albero_motore = partizione(codice_motore,PLM_BOM)
        indice_inizio = indice_motore
        indice_fine = indice_motore + len(albero_motore)

        # elimino livelli 3 (oppure Item Type == Engine Functional Group) e faccio salire di 1 tutti gli altri tranne il livello 2
        albero_motore['eliminare'] = False
        for i in range (len (albero_motore)):
            if albero_motore.loc[i+indice_inizio,'Articolo'] == codice_motore:
                pass
            elif albero_motore.loc[i+indice_inizio,'Liv.'] == 3:
                albero_motore.loc[i+indice_inizio,'eliminare'] = True
            else:
                albero_motore.loc[i+indice_inizio,'Liv.'] = albero_motore.loc[i+indice_inizio,'Liv.']-1

        # assegno i gruppi tecnici al motore
        for i in range(1,len(albero_motore)):
            if albero_motore.eliminare.iloc[i]==True:
                gruppo_tecnico = albero_motore.Articolo.astype(str).iloc[i][:2]+'.'
                des_gruppo = albero_motore['Testo breve oggetto'].iloc[i]
            albero_motore['Gruppo Tecnico'].iloc[i]=gruppo_tecnico
            albero_motore['Descr. Gruppo Tecnico'].iloc[i]=des_gruppo
                
        albero_motore_processato = albero_motore[albero_motore['eliminare']==False]
        albero_motore_processato.drop(columns=['eliminare'], inplace=True)
        albero_motore_processato.reset_index(inplace=True, drop=True)
    return albero_motore_processato

def compara_strutture_piattaforme(albero_SAP, albero_PLM):
    
    albero_SAP = albero_SAP.rename(columns={'Liv.':'livello','Articolo':'articolo','Testo breve oggetto':'descrizione','Qty':'Qty SAP'})
    albero_SAP = albero_SAP[['livello','articolo','descrizione','Qty SAP','key']] # mantenute qty
    albero_PLM = albero_PLM.rename(columns={'Liv.':'livello','Articolo':'articolo','Testo breve oggetto':'descrizione','Qty':'Qty PLM'})
    albero_PLM = albero_PLM[['livello','articolo','descrizione','Qty PLM','key']] # mantenute qty   
    
    albero_PLM['Liv'] = [int(stringa[-1]) for stringa in albero_PLM['livello'].astype(str)]
    albero_PLM=albero_PLM.drop('livello',axis=1)
    albero_SAP['Liv'] = [int(stringa[-1]) for stringa in albero_SAP['livello'].astype(str)]
    albero_SAP = albero_SAP.drop('livello',axis=1)

    albero_PLM_sum = albero_PLM[['key','Qty PLM']].groupby(by='key').sum()
    albero_PLM_sum = albero_PLM_sum.rename(columns={'Qty PLM':'Totale_PLM'})
    albero_SAP_sum = albero_SAP[['key','Qty SAP']].groupby(by='key').sum()
    albero_SAP_sum = albero_SAP_sum.rename(columns={'Qty SAP':'Totale_SAP'})

    albero_SAP = albero_SAP.merge(albero_SAP_sum, how='left',left_on='key',right_on='key')
    albero_PLM = albero_PLM.merge(albero_PLM_sum, how='left',left_on='key',right_on='key')

    #sap_new = albero_SAP.merge(albero_PLM, how='left',left_on='articolo',right_on='articolo')
    sap_new = albero_SAP.merge(albero_PLM, how='left',left_on='key',right_on='key')

    sap_new['riportato'] = np.where(sap_new.descrizione_y.astype(str)=='nan','si',None)

    albero_PLM['new_index']=None
    for i in range(len(albero_PLM)):
        albero_PLM['new_index'].iloc[i]=100*i    
        
    sap_new['padre_plm']=None
    for i in range(len(sap_new)):
        n=0
        if sap_new.riportato.iloc[i]=='si':
            for j in range(20):
                if sap_new.riportato.astype(str).iloc[i-j] == 'None':               
                    key = sap_new.key.iloc[i-j]
                    indice_plm = albero_PLM[albero_PLM.key == key].index[0]
                    sap_new.padre_plm.iloc[i] = indice_plm*100 +1
                    sap_new['Liv_x'].iloc[i]=None
                    break

    to_append = sap_new[['articolo_y','descrizione_y','Liv_x','padre_plm','Qty SAP','key']][sap_new.riportato=='si']
    to_append = to_append.rename(columns={'descrizione_y':'descrizione','Liv_x':'Liv','padre_plm':'new_index'})
    albero_PLM = pd.concat([albero_PLM,to_append])  
    albero_PLM = albero_PLM.sort_values(by='new_index')
    albero_PLM = albero_PLM.drop(columns=['articolo_y','Qty SAP'])
    plm_new = albero_PLM.merge(albero_SAP, how='left',left_on='key',right_on='key')
    plm_new['Articolo'] = np.where(plm_new.articolo_x.astype(str) != 'nan', plm_new.articolo_x, plm_new.articolo_y)

    plm_new = plm_new.rename(columns={'descrizione_x':'descrizione_PLM','Liv_x':'Liv_PLM','descrizione_y':'descrizione_SAP','Liv_y':'Liv_SAP','Qty SAP_y':'Qty SAP','Totale_SAP_x':'Totale_SAP'})
    plm_new.drop(columns=['new_index','key','articolo_x','articolo_y'], axis=1, inplace=True)
    plm_new = plm_new[['Articolo','descrizione_PLM','Qty PLM','Liv_PLM','descrizione_SAP','Qty SAP','Liv_SAP','Totale_PLM','Totale_SAP']]
    return plm_new

def add_padre(df):
    # la funzione prende in ingresso un albero (df) di distinta e accanto a ogni codice scrive il nome di suo padre
    df['Padre']=None
    for i in range(1, len(df)):
        livello = df['Liv.'].iloc[i]
        if livello == 3:
            df.Padre.iloc[i]= 'motore'
        else:
            j=1        
            while df['Liv.'].iloc[i-j] >= livello:
                j+=1
            else:
                padre = df.Articolo.iloc[i-j]
                df.Padre.iloc[i]=padre
                continue

    df.Padre.iloc[0] = 'Nessuno'
    df['key']=df.Articolo + ' figlio di ' + df.Padre
    return df

def color_mancante(val):
    color = 'grey' if str(val)=='nan' or str(val)=='<NA>' else 'black'
    return f'background-color: {color}'

def visualizza_appaiato(piattaforma_SAP, piattaforma_PLM, lay='bom_appaiate'):    
    piattaforma_SAP_2 = add_padre(piattaforma_SAP)
    piattaforma_PLM_2 = add_padre(piattaforma_PLM)
    piattaforme_compare = compara_strutture_piattaforme(piattaforma_SAP_2,piattaforma_PLM_2)   
    piattaforme_compare['Liv_PLM'] = piattaforme_compare['Liv_PLM'].astype('Int64')
    piattaforme_compare['Liv_SAP'] = piattaforme_compare['Liv_SAP'].astype('Int64')
    piattaforme_compare['Delta_Qty'] = piattaforme_compare['Qty PLM'] - piattaforme_compare['Qty SAP']
    piattaforme_compare['Delta_Tot'] = piattaforme_compare['Totale_PLM'] - piattaforme_compare['Totale_SAP']   
    piattaforme_compare = piattaforme_compare[((piattaforme_compare.Delta_Tot == 0) & (piattaforme_compare.Delta_Qty != 0))==False]
    #piattaforme_compare.drop_duplicates(inplace=True)
    piattaforme_compare['Indentato'] = [(livello-2)* 10 * ' ' if str(livello) != '<NA>' else None for livello in piattaforme_compare['Liv_PLM']]
    piattaforme_compare['descrizione_PLM'] = piattaforme_compare.Indentato + piattaforme_compare.descrizione_PLM
    piattaforme_compare['Indentato_SAP'] = [(livello-2)* 10 * ' ' if str(livello) != '<NA>' else None for livello in piattaforme_compare['Liv_SAP']]
    piattaforme_compare['descrizione_SAP'] = piattaforme_compare.Indentato_SAP + piattaforme_compare.descrizione_SAP
    st.dataframe(piattaforme_compare[layout[lay]].style.applymap(color_mancante, subset=['descrizione_PLM','descrizione_SAP','Liv_PLM','Liv_SAP','Qty SAP','Qty PLM']), width=2000)
    #st.dataframe(piattaforme_compare[layout[lay]].style.applymap(color_mancante), width=2500)
    #st.write('Non in PLM:', len(piattaforme_compare[piattaforme_compare.descrizione_PLM.astype(str) == 'nan']))
    #st.write('Non in SAP:', len(piattaforme_compare[piattaforme_compare.descrizione_SAP.astype(str) == 'nan']))
    #deltaqty=piattaforme_compare[piattaforme_compare.Delta_Qty != 0].drop(columns=['Indentato','Indentato_SAP'],axis=1)
    #st.write('Correggere qty:',len(deltaqty[deltaqty.Delta_Qty.astype(str)!='nan']))

def confronta_no_figli(sap, plm):
    agg_sap = sap[['Articolo','Testo breve oggetto','Qty']].groupby(by=['Articolo','Testo breve oggetto'], as_index=False).sum()
    agg_plm = plm[['Articolo','Testo breve oggetto','Qty']].groupby(by=['Articolo','Testo breve oggetto'], as_index=False).sum()
    confronto = agg_sap.merge(agg_plm, how='left',left_on='Articolo',right_on='Articolo', suffixes=('_SAP','_PLM'))
    confronto['Qty_PLM']= confronto['Qty_PLM'].fillna(0)
    confronto['∆'] = confronto['Qty_PLM'] - confronto['Qty_SAP']
    before = len(confronto)
    confronto = confronto[confronto['∆']!=0]
    after = len(confronto)
    return confronto, before, after








