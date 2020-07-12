# importation des modules
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import pandas as pd
from readability import Readability
import pandas as pd,os

import plotly.offline as pyo
import plotly.graph_objs as go
import numpy as np
import pandas as pd, time

import base64
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import dash_cytoscape as cyto

from os import walk
import nltk
nltk.download('punkt')




# creation d'une file d'attente
#from rq import Queue
#from worker import conn
#from redis import Redis

#q = Queue(connection=conn)

#from utils import count_words_at_url

#result = q.enqueue(count_words_at_url, 'http://heroku.com')






UPLOAD_DIRECTORY = "./dossiertext"

server = Flask(__name__)
#app = dash.Dash(server=server)

app = dash.Dash(server=server,external_stylesheets=[dbc.themes.BOOTSTRAP])


for (repertoire, sousRepertoires, fichiers) in walk("./assets/repertoire_pdf"):
             repertoire_pdf = fichiers

for (repertoire, sousRepertoires, fichiers) in walk("./assets/example_pdf"):
             example_pdf = fichiers

for (repertoire, sousRepertoires, fichiers) in walk("./assets/data"):
             data = fichiers 

# une fonction pour la transformation d'un fichier pdf en fichier texte
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

# Une fonction de calcul des indices de lisibilité
# le resultat est donné sous la forme d'un dictionnaire

def fcts(nom_fichier):
    # nom_fichier est le nom du fichier qui fera l'objet d'un calcul sur sa lisibilité
    
    # convertion du fichier en fichier txt
    nom_fichier_ = convert_pdf_to_txt(nom_fichier)
    
    # Decoupage du fichier txt converti en plusieurs morceaux en ayant pour critère de découpage, les
    # parties des paragraphes qui sont séparées par un retour à la ligne deux fois
    x=nom_fichier_.split('\n\n')
    
    # Pour chaque fichier découpé, on supprime les retours à la ligne
    y = [x[i].replace('\n',' ') for i in range(len(x))]
    
    # on réunit tous les fichiers découpés en un seul fichier dans une variable z
    z = ' '.join(y)
    
    # on crée un fichier vide nommé texte.txt
    f = os.open('texte.txt',os.O_CREAT)
    
    # on recopie le contenu de la variable z dans le fichier texte.txt et ce afin d'utiliser les 
    #modules python qui sont adaptés aux traitements de fichiers
    with open('texte.txt','w') as f :
        f.write(z)
        
    # le fichier texte.txt est un fichier brute qui contient toutes sortes de caractères
           # ouverture du fichier texte.txt en mode écriture et binaire
    q = open('texte.txt', "rb")
    
    # lecture du fichier texte.txt en ignorant les caractères ou mots non lisibles
    text = q.read().decode(errors='ignore')
    
    # effacer le contenu du fichier texte.txt pour s'assurer que si cette fonction fct est utilisée
    # pour un traitement automatique, chaque entrée de nouveau fichier canditat pour une opération pdf to txt
    # soit enrégistré dans un fichier vierge nommé de format txt 
    with open('texte.txt','w') as f :
        f.write(' ')
    os.remove('texte.txt')
    
        
    # la lecture des caractères illisibles ignorés, le texte est maintenant propre
    # pour ses résultats de lisibilité dans le package Readability
    r = Readability(text)
    
    # colonnes du fichier csv définie
    col = ["Year","Company","Flesch Kincaid score","Fog grade level","Flesh ease",\
          "Flesch score","Fog score","Flesch grade level","Flesch Kincaid grade level"]
    # traitement pour un fichier
          # chaque fichier doit porter le nom de l'entreprise suivi de '_' suivi de l'année
        
    company = ' '.join(nom_fichier[:-4].split('_')[:-1])
    year = nom_fichier[:-4].split('_')[-1]
    
    # recupération des attributs ou instances de Readability dans des variables
    fks = round(r.flesch_kincaid().__dict__['score'],3) # Flesch Kincaid score
    fogg = r.gunning_fog().__dict__['grade_level'] # Fog grade level
    fe = r.flesch().__dict__['ease'] # flesch ease
    fs = round(r.flesch().__dict__['score'],3) # flesch score
    fogs = round(r.gunning_fog().__dict__['score'],3) # Fog score 
    fg = r.flesch().__dict__['grade_levels'][0] # flesch grade level ### liste
    fkg = float((r.flesch_kincaid().__dict__['grade_level'])) # Flesch Kincaid grade level
    
    # les valeurs de ces variables sont récupérées dans une liste appelée résultat
    resultat = [year,company,fks,fogg,fe,fs,fogs,fg,fkg]
    
    # sortie du résultat sous forme de dictionnaire
    return {col[i]:resultat[i] for i in range(len(col))}

# traitement automatique
def trait_aut(*dic):
    frames = pd.concat([pd.DataFrame(dic[i]) for i in range(len(dic))])
    frames.index = range(len(frames))
    return frames# importation des modules



col = ["Year","Company","Flesch Kincaid score","Fog grade level","Flesh ease",\
          "Flesch score","Fog score","Flesch grade level","Flesch Kincaid grade level"]


# recuperation des rapports
#rap = os.listdir("./assets/repertoire_pdf/")

rap = repertoire_pdf
#os.chdir("./../../")
#os.chdir()
PAGE_SIZE = 10
years = list(set([rap[i][:-4].split('_')[-1] for i in range(len(rap))]))

years = sorted(years)

# recuperation des entreprises
companiess = [' '.join(rap[i][:-4].split('_')[:-1]) for i in range(len(rap))]
companies = list(set(companiess)) # unique

# recuperation des differentes annees pour chaque entreprise

comp = []; comp_yr = {}
for c in range(len(companiess)) :
    if companiess[c] not in comp :
        comp.append(companiess[c])
        comp_yr[companiess[c]] = [ companiess.index(companiess[c])]
    else :
        comp_yr[companiess[c]].append(companiess[c:].index(companiess[c]) + c )
comp_yrs = {c:[rap[comp_yr[c][i]][:-4].split('_')[-1] for i in range(len(comp_yr[c]))] for c in comp_yr }

comp_yrs  = {c : sorted(comp_yrs[c]) for c in comp_yrs}
        
# btn du traitement automatique
      # traitement automatique
    
##################################"""""""""""###"""
##############################################""""""

    #contenaire de toute la page treatment
app.layout = html.Div([
    # traitement automatique
        # une ligne pour les boutons
    html.Div([
           # boutons traitement automatique
            
        html.Div([
            dbc.Button("Traitement automatique",'id_trait' ,outline=True, color="primary", className="mr-1"),
        ],style = {'display':'inline-block','width':'20%','float':'left','padding':7}),
        
              
        # nom du fichier
        
        html.Div( [html.Div("nom du fichier sans .csv",style = {'color':'white'}),
            dcc.Input(id='my-id', value='nom_du_fichier', type='text'),
                    html.Div(id='my-div')],style = {'display':'inline-block','width':'20%'} ),
        
        
                #telecharger
        #dcc.Loading( children=[html.Div(id="loading-output-1")], type="default")
        
        html.Div([html.Div([dbc.Button("télécharger", id = 'id_telecharger',outline=True,
            color="success", className="mr-1"),
        #dbc.Spinner(html.Div(id="loading-output",style = {"textAlign": "center",'color':'white'}))
        dcc.Loading( children=[html.Div(id="loading-output",
                            style = {"textAlign": "center",'color':'white'})], type="default")
        
                            
                           ]),],
                 #style = {'display':'inline-block','width':'20%'}),],
        style = {'display':'inline-block', 'width':'20%'}
        ),
        
      #  html.Div([
        html.Div([html.Div('selectionner data',style = {'color':'white','padding':0.5}),
                  html.Div(dcc.Dropdown(
                      
                id='id_csv',
                options=[{"label": i, "value": i} for i in ["aucun fichier"] + data 
                #for _, _, i in walk("./assets/data")#data 
                ],
                value = "aucun fichier"))],
                 style = {'display':'inline-block','width':'20%','float': 'right'} ),
   
            
            #dbc.Button("zone de texte", outline=True, color="warning", className="mr-1"),],
                 #style = {'display':'inline-block','width':'20%'}),
        
        # supprimer un fichier
        
        html.Div([dbc.Button("supprimer le fichier",id = "id_supprimer", outline=True, color="info", className="mr-1"),]
                 ,style = {'display':'inline-block','width':'20%','float': 'right' })],
           # style = {'display':'inline-block','width':'100%'})]
        
    style = {'background-color': 'black','height' :'150','padding':5} ),
                
                html.Div([
        
        dash_table.DataTable(
    id='id_dfs',
    columns=[
        {"name": i, "id": i} for i in col
    ],
    page_current=0,
    page_size=PAGE_SIZE,
    page_action='custom'
) 
        # cadre du contenaire cl4
    ],style = {'width':'25%','padding':'1%','margin':'0.05%'
              }
    
    ),
     html.Div(
    [
        #dbc.Button("Load", id="loading-button"),
        #dbc.Spinner(html.Div(id="loading-output")),
    ], style = {}
)

    
],style = {'width':'100%','padding':'10px','margin':'10px'
                },
)

    
    
#],
    # cadre contenaire de la page treatment
#    style = {'width':'100%','height':'100%','background-color': 'white'}
#)


#@app.callback(
 #   Output("contenu_du_texte", "is_open"), # 'contenu_du_texte' positioned-toast
  #  [Input("positioned-toast-toggle", "n_clicks")],
#)
#def open_toast(n):
 #   if n:
  #      return True
   # return False
    
#@app.callback(
 #   Output("modal-centered", "is_open"),
  #  [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
   # [State("modal-centered", "is_open")])

#def toggle_modal(n1, n2, is_open):
 #   if n1 or n2:
  #      return not is_open

   # return is_open


#@app.callback(
 #   Output('id_pdf_cadre', 'children'),[Input('id_liste_pdf', "value")])
 #id_pdf_cadre est desormais identifié comme le nom du fichier de id_liste_pdf

#def affichePDF(nom_fichier):
#    if nom_fichier is not None and len(nom_fichier) > 0 :
        #nom_fichier = nom_fichier
 #       return   nom_fichier 


###################     ###    ##################        #################   ###############   #############


# Une fonction de calcul des indices de lisibilité
# le resultat est donné sous la forme d'un dictionnaire

def fct(nom_fichier):
    # nom_fichier est le nom du fichier qui fera l'objet d'un calcul sur sa lisibilité
    
    # convertion du fichier en fichier txt
    nom_fichier_ = convert_pdf_to_txt(nom_fichier)
    
    # Decoupage du fichier txt converti en plusieurs morceaux en ayant pour critère de découpage, les
    # parties des paragraphes qui sont séparées par un retour à la ligne deux fois
    x=nom_fichier_.split('\n\n')
    
    # Pour chaque fichier découpé, on supprime les retours à la ligne
    y = [x[i].replace('\n',' ') for i in range(len(x))]
    
    # on réunit tous les fichiers découpés en un seul fichier dans une variable z
    z = ' '.join(y)
    
    # on crée un fichier vide nommé texte.txt
    f = os.open('texte.txt',os.O_CREAT)
    
    # on recopie le contenu de la variable z dans le fichier texte.txt et ce afin d'utiliser les 
    #modules python qui sont adaptés aux traitements de fichiers
    with open('texte.txt','w') as f :
        f.write(z)
        
    # le fichier texte.txt est un fichier brute qui contient toutes sortes de caractères
           # ouverture du fichier texte.txt en mode écriture et binaire
    q = open('texte.txt', "rb")
    
    # lecture du fichier texte.txt en ignorant les caractères ou mots non lisibles
    text = q.read().decode(errors='ignore')
    
    # effacer le contenu du fichier texte.txt pour s'assurer que si cette fonction fct est utilisée
    # pour un traitement automatique, chaque entrée de nouveau fichier canditat pour une opération pdf to txt
    # soit enrégistré dans un fichier vierge nommé de format txt 
    with open('texte.txt','w') as f :
        f.write(' ')
    os.remove('texte.txt')
        
    # la lecture des caractères illisibles ignorés, le texte est maintenant propre
    # pour ses résultats de lisibilité dans le package Readability
    r = Readability(text)
    
    # colonnes du fichier csv définie
    col = ["Year","Company","Flesch Kincaid score","Fog grade level","Flesh ease",\
          "Flesch score","Fog score","Flesch grade level","Flesch Kincaid grade level"]
    # traitement pour un fichier
          # chaque fichier doit porter le nom de l'entreprise suivi de '_' suivi de l'année
        
    company = ' '.join(nom_fichier[:-4].split('_')[:-1])
    year = nom_fichier[:-4].split('_')[-1]
    
    # recupération des attributs ou instances de Readability dans des variables
    fks = round(r.flesch_kincaid().__dict__['score'],3) # Flesch Kincaid score
    fogg = r.gunning_fog().__dict__['grade_level'] # Fog grade level
    fe = r.flesch().__dict__['ease'] # flesch ease
    fs = round(r.flesch().__dict__['score'],3) # flesch score
    fogs = round(r.gunning_fog().__dict__['score'],3) # Fog score 
    fg = r.flesch().__dict__['grade_levels'] # flesch grade level ### liste
    fkg = float((r.flesch_kincaid().__dict__['grade_level'])) # Flesch Kincaid grade level
    
    # les valeurs de ces variables sont récupérées dans une liste appelée résultat
    #resultat = [year,company,fks,fogg,fe,fs,fogs,fg,fkg]
    
    # sortie du résultat sous forme de dictionnaire
    return year,company,fks,fogg,fe,fs,fogs,fg,fkg,text #{col[i]:resultat[i] for i in range(len(col))}


#@app.callback(
    
#[Output('m_year', 'children'),Output("m_company", "children"),
 #Output("m_Flesch_Kincaid_score", "children"),Output("m_Fog_grade_level", "children"),
 #Output("m_Flesh_ease", "children"),Output("m_Flesch_score", "children"),
 #Output("m_Fog_score", "children"),Output("m_Flesch_grade_level", "children"),
# Output("m_Flesch_Kincaid_grade_level", "children"),Output("contenu_du_texte", "children")],
    
#[Input('id_pdf_cadre', "children")],
    
#[State('m_year', 'children'),State("m_company", "children"),
 #State("m_Flesch_Kincaid_score", "children"),State("m_Fog_grade_level", "children"),
 #State("m_Flesh_ease", "children"),State("m_Flesch_score", "children"),
 #State("m_Fog_score", "children"),State("m_Flesch_grade_level", "children"),
# State("m_Flesch_Kincaid_grade_level", "children"),
# State("contenu_du_texte", "children")
#] )

   # col = ["Year","Company","Flesch Kincaid score","Fog grade level","Flesh ease",\
    #      "Flesch score","Fog score","Flesch grade level","Flesch Kincaid grade level"]

def affiche_pdf(pdf,year,company,fks,fogg,fe,fs,fogs,fg,fkg,texte):
    if pdf is not None and len(pdf) > 0 :
 
        year,company,fks,fogg,fe,fs,fogs,fg,fkg,texte = fct("./assets/repertoire_pdf/{}".format(pdf))
        return [year],[company[24:]],[fks],[fogg],[fe],[fs],[fogs],[fg[0]],[fkg],[texte]
        
# changement de  pdf

#@app.callback( Output('id_pdf','src'),[Input('id_pdf_cadre','children')] )

def update_data(new_pdf):
    if new_pdf is not None and len(new_pdf) > 0 :
        return "./assets/repertoire_pdf/{}".format(new_pdf)
    
    
# gestion de la partie traitement automatique


@app.callback(
    Output('id_dfs', 'data'),
    
    [Input("id_trait", "n_clicks"),Input('id_dfs', "page_current"),
     Input('id_dfs', "page_size")],[State('my-id','value')])
    
   
def Trait_aut(n,page_current, page_size,csv_):
    raps = example_pdf
    if n is None:
            return "Not clicked."
        
    if csv_ is [None or "aucun fichier"]:
                    return "Not clicked."
    #if csv_ in os.listdir():
    if csv_ in data:

        k = csv.iloc[ page_current*page_size:(page_current+ 1)*page_size].to_dict('records')
        return k
        
    else:
        #os.chdir("./assets/repertoire_pdf/")
        m = len(raps)
        doss = [fcts("./assets/example_pdf/"+raps[i]) for i in range(m)]
        for i in range(m):
            doss[i]['Company'] = doss[i]['Company'].split('/')[-1]
        dx = trait_aut(doss)
        k = dx.iloc[ page_current*page_size:(page_current+ 1)*page_size].to_dict('records')
        return  k


@app.callback(#Output("id_telecharger", "children"),
    Output('my-div','children'),[Input("id_telecharger", "n_clicks")],
    [State('my-id','value')]
    )
    
def download(n1,val):
    if n1 is not None :
        m = len(rap)
        doss = [fcts("./assets/repertoire_pdf/"+rap[i]) for i in range(m)]
        for i in range(m):
            doss[i]['Company'] = doss[i]['Company'].split("/")[-1]
        dx = trait_aut(doss)
        dx.to_csv("./assets/data/{}.csv".format(val),index=False)

@app.callback(Output('id_csv','value'),[Input("id_supprimer", "n_clicks")],[State('id_csv','value')])

def suppression(n,csv):
    if n is not None and csv not in ['aucun fichier', None] :
        #ind = os.listdir("./assets/data/").index(csv)
        try :
            fich = "./assets/data/" + csv
            os.remove(fich)
            
        except FileNotFoundError :
            print('fichier ',csv, ' supprimé!')
        except TypeError:
            print(csv, ' n\'est pas un fichier!')        
    #return os.listdir("./assets/data/")
    return [i for _, _, i in walk("./assets/data")]




@app.callback(
    #Output("loading-output", "children"), [Input("loading-button", "n_clicks")]
    #[Output('my-div','children'),
     Output("loading-output", "children")
    #]
    ,[Input("id_telecharger", "n_clicks")],[State('my-id','value')])

def load_output(n,nomf):
	# liste des fichiers du repertoire courant
	#os.listdir(os.getcwd())

    if n:
        #time.sleep(15)
        #if "{}".format("Entrer le nom") is 


        return "Vous avez télécharger le fichier: {}".format(nomf )
    return "Télécharger le fichier {}".format(nomf)
        
       
if __name__ == '__main__' :
    app.run_server()

# TEMPS D'ATTENTE
#https://devcenter.heroku.com/articles/python-rq
#https://devcenter.heroku.com/articles/background-jobs-queueing
# https://python-rq.org/docs/

#https://discuss.erpnext.com/t/error-111-connecting-to-localhost/4726/3

         # H10
  #https://dev.to/lawrence_eagles/causes-of-heroku-h10-app-crashed
     #-error-and-how-to-solve-them-3jnl#:~:text=This%20error%20is%20thrown%20if,App%20crashed%20error%20code%20message.

     #https://www.digitalocean.com/community/tutorials/how-to-set-up-
        #django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04#creating-systemd-socket-and-service-files-for-gunicorn
       #https://dash.plotly.com/deployment


       #redis-server.service: Can't open PID file /var/run/redis/redis-server.pid (yet?) after start: No such file or diretory
                       # deployer une application sur github
       #https://docs.oracle.com/en/cloud/paas/app-container-cloud/node-github-accs/index.html
                       # deployement - un probleme a resoudre
       # https://stackoverflow.com/questions/4181861/message-src-refspec-master-does-not-match-any-when-pushing-commits-in-git