import datetime
import os.path
import sqlite3

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



#PERSONNALISATION AFFICHAGE
hauteur_bouton=40
hauteur_petit_bouton=35
longueur_bouton=400
longueur_petit_bouton=150
col_bouton='#F27C00'



col_fond='#E8DFB1'
col_police_basique='#002F48'






# Initialisation de la fenetre d'affichage
window=Tk()



# Connexion à la base de données locale
con = sqlite3.connect("MonEntreprise.db")




# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]



# Initialisations de variables
entry_an=StringVar()
entry_moisd=StringVar()
entry_moisf=StringVar()

entry_titre=StringVar()
combobx_periodicite=StringVar()
entry_montant=StringVar()

entry_modif_titre=StringVar()
combobx_modif_periodicite=StringVar()
entry_modif_montant=StringVar()










###################################################################################






### CLASSE POUR LA FRAME AVEC SCROLL VERTICAL ET HORIZONTAL
class DoubleScrolledFrame:
    """
    A vertically scrolled Frame that can be treated like any other Frame
    ie it needs a master and layout and it can be a master.
    keyword arguments are passed to the underlying Frame
    except the keyword arguments 'width' and 'height', which
    are passed to the underlying Canvas
    note that a widget layed out in this frame will have Canvas as self.master,
    if you subclass this there is no built in way for the children to access it.
    You need to provide the controller separately.
    """
    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        self.outer = Frame(master, **kwargs)

        self.vsb = ttk.Scrollbar(self.outer, orient=VERTICAL)
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.hsb = ttk.Scrollbar(self.outer, orient=HORIZONTAL)
        self.hsb.grid(row=1, column=0, sticky='ew')
        self.canvas = Canvas(self.outer, highlightthickness=0, width=width, height=height)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.outer.rowconfigure(0, weight=1)
        self.outer.columnconfigure(0, weight=1)
        self.canvas['yscrollcommand'] = self.vsb.set
        self.canvas['xscrollcommand'] = self.hsb.set
        # mouse scroll does not seem to work with just "bind"; You have
        # to use "bind_all". Therefore to use multiple windows you have
        # to bind_all in the current widget
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview
        self.hsb['command'] = self.canvas.xview

        self.inner = Frame(self.canvas)
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()
        self.canvas.config(scrollregion = (0,0, max(x2, width), max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        func = self.canvas.xview_scroll if event.state & 1 else self.canvas.yview_scroll 
        if event.num == 4 or event.delta > 0:
            func(-1, "units" )
        elif event.num == 5 or event.delta < 0:
            func(1, "units" )
    
    def __str__(self):
        return str(self.outer)






###################################################################################






# Récupérer et afficher les données du calendrier
def get_data():
    
    

    # MISE EN PLACE DE L'API

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
             "credentials.json", SCOPES
         )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())





    for widget in frameaffich.winfo_children() :
        widget.destroy()

    frameaffich_get_data= Frame(frameaffich, bg=col_fond)
    frameaffich_get_data.pack(fill=BOTH, expand=True)
    
    frameaffichspe= DoubleScrolledFrame(frameaffich_get_data, height=400, width=800, borderwidth=2, relief=SUNKEN, bg=col_fond)
    frameaffichspe.canvas.configure(bg=col_fond)
    frameaffichspe.inner.configure(bg=col_fond)
    frameaffichspe.pack(fill=BOTH, expand=True)
    
    
    # DEBUT DU TRAVAIL SUR LE CALENDRIER
    try:
        
        cur = con.cursor()
        
        service = build("calendar", "v3", credentials=creds)

        an = int(entry_an.get())
        moisd = int(entry_moisd.get())
        moisf = int(entry_moisf.get())
        if moisf==12 :
            moisf=1
            anf=an+1
        else :
            moisf=moisf+1
            anf=an


        #Extraction de toutes les infos
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = (
            service.events()
            .list(
                timeMin=datetime.datetime(year=an, month=moisd, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc).isoformat(),
                timeMax=datetime.datetime(year=anf, month=moisf, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc).isoformat(),
                calendarId="primary",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        #Notre Dictionnaire que nous allons exploiter
        M={}
        H=0

        for event in events :
            s=event["summary"]
            dd=event["start"]["dateTime"]
            df=event["end"]["dateTime"]
            if s not in M:
                M[s]=[datetime.timedelta(hours=0),[]]
            M[s][1].append((dd,df))
            M[s][0]= M[s][0] + datetime.timedelta(hours=int(df[11:13])) + datetime.timedelta(minutes=int(df[14:16])) - datetime.timedelta(hours=int(dd[11:13])) - datetime.timedelta(minutes=int(dd[14:16]))

        #Conversion du temps de cours de seconds en heures
        for s in M :
            M[s][0]= M[s][0].total_seconds()/3600


        #Affichage des infos du calendrier
        e=0
        k=0
        for nom in M :

            labelnom= Label(frameaffichspe, text=nom+" : ", bg=col_fond, fg=col_police_basique)
            labelnom.grid(row=k, column=0)
            frameaffichspe.inner.columnconfigure(0, pad=20)

            H=H+M[nom][0]
            
            t=cur.execute(""" SELECT periodicite_paiement, taux FROM taux_horaires WHERE titre = ?""", [nom]).fetchone()
            if t[0]=="mensuel" :
                labelprix= Label(frameaffichspe, text=str(t[1])+" €", bg=col_fond, fg=col_police_basique)
                labelprix.grid(row=k, column=1)
                e=e+t[1]

            if t[0]=="horaire" :
                T=M[nom][0]*t[1]
                e=e+T
                labelprix= Label(frameaffichspe, text=str(T)+" €", bg=col_fond, fg=col_police_basique)
                labelprix.grid(row=k, column=1)
            frameaffichspe.inner.columnconfigure(1, pad=20)

            labelnbh= Label(frameaffichspe, text=str(M[nom][0])+"h", bg=col_fond, fg=col_police_basique)
            labelnbh.grid(row=k, column=2)
            frameaffichspe.inner.columnconfigure(2, pad=20)


            #Dates
            for i in range(len(M[nom][1])) :
                dd=M[nom][1][i][0]
                df=M[nom][1][i][1]
                duree=datetime.timedelta(hours=int(df[11:13])) + datetime.timedelta(minutes=int(df[14:16])) - datetime.timedelta(hours=int(dd[11:13])) - datetime.timedelta(minutes=int(dd[14:16]))
                duree=duree.total_seconds()/3600

                if duree==1:
                    labeldate= Label(frameaffichspe, text=str(dd[8:10])+"/"+str(dd[5:7]), bg='#FFFFB4', fg=col_police_basique)
                    labeldate.grid(row=k, column=3+i)
                if duree==1.5:
                    labeldate= Label(frameaffichspe, text=str(dd[8:10])+"/"+str(dd[5:7]), bg='#FF9632', fg=col_police_basique)
                    labeldate.grid(row=k, column=3+i)
                if duree==2:
                    labeldate= Label(frameaffichspe, text=str(dd[8:10])+"/"+str(dd[5:7]), bg='#FF0000', fg=col_police_basique)
                    labeldate.grid(row=k, column=3+i)
                if duree!=1 and duree!=1.5 and duree!=2:
                    labeldate= Label(frameaffichspe, text=str(dd[8:10])+"/"+str(dd[5:7]), bg='#2773F5', fg=col_police_basique)
                    labeldate.grid(row=k, column=3+i)
                frameaffichspe.inner.columnconfigure(3+i, pad=20)
            
            frameaffichspe.inner.rowconfigure(k, pad=10)
            k=k+1

        #Total et légende
        labeltotal= Label(frameaffichspe, text="Total : "+str(e)+" €", bg='#D22727', fg=col_fond)
        labeltotal.grid(row=k+1, column=0, columnspan=2)

        labeltotal= Label(frameaffichspe, text="Nb d'heures : "+str(H)+" h", bg='#D22727', fg=col_fond)
        labeltotal.grid(row=k+1, column=2,columnspan=5 )

        frameaffichspe.inner.rowconfigure(k+1, pad=30)

        labellegende= Label(frameaffichspe, text="Légende :", bg=col_fond, fg=col_police_basique)
        labellegende.grid(row=k+3, column=0)
        labellegende= Label(frameaffichspe, text="1h", bg='#FFFFB4', fg=col_police_basique)
        labellegende.grid(row=k+3, column=1)
        labellegende= Label(frameaffichspe, text="1h30", bg='#FF9632', fg=col_police_basique)
        labellegende.grid(row=k+3, column=2)
        labellegende= Label(frameaffichspe, text="2h", bg='#FF0000', fg=col_police_basique)
        labellegende.grid(row=k+3, column=3)
        labellegende= Label(frameaffichspe, text="autre", bg='#2773F5', fg=col_police_basique)
        labellegende.grid(row=k+3, column=4)




        cur.close()

    #Gestion des erreurs
    except HttpError as error:
        print(f"An error occurred: {error}")







#Demander les infos nécessaire pour savoir que chercher dans le calendrier
def infos_get_data () :
    for widget in frameaffich.winfo_children() :
        widget.destroy()
        
    frameaffich_infos_get_data= Frame(frameaffich, bg=col_fond)
    frameaffich_infos_get_data.pack(fill=BOTH, expand=True)
    
    framean= Frame(frameaffich_infos_get_data, bg=col_fond, borderwidth=15)
    framemoisd= Frame(frameaffich_infos_get_data, bg=col_fond, borderwidth=15)
    framemoisf= Frame(frameaffich_infos_get_data, bg=col_fond, borderwidth=15) 

    labelan=Label(framean, text="Choisir l'année :", bg=col_fond, fg=col_police_basique)   
    entry_tk_an=Entry(framean, width=40, textvariable=entry_an)

    labelmoisd=Label(framemoisd, text="Numéro du premier mois de facture :", bg=col_fond, fg=col_police_basique)
    entry_tk_moisd=Entry(framemoisd, width=40, textvariable=entry_moisd)

    labelmoisf=Label(framemoisf, text="Numéro du dernier mois de facture :", bg=col_fond, fg=col_police_basique)
    entry_tk_moisf=Entry(framemoisf, width=40, textvariable=entry_moisf)

    binfos_get_data=Button(frameaffich_infos_get_data, text="Valider", image=pixel, command=get_data, bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_bouton, height=hauteur_bouton, compound="c")
    
    for i in range (4) :
        frameaffich_infos_get_data.grid_rowconfigure(i, weight=1)
        frameaffich_infos_get_data.rowconfigure(i, pad=20)

    frameaffich_infos_get_data.grid_columnconfigure(0, weight=1)
    framean.grid(row=0, column=0, sticky="nsew")
    framemoisd.grid(row=1, column=0, sticky="nsew")
    framemoisf.grid(row=2, column=0, sticky="nsew")
    labelan.pack()
    entry_tk_an.pack()
    labelmoisd.pack()
    entry_tk_moisd.pack()
    labelmoisf.pack()
    entry_tk_moisf.pack()
    binfos_get_data.grid(row=3, column=0)







def taux_horaire() :
    for widget in frameaffich.winfo_children() :
        widget.destroy()
        
    frameaffich_taux_horaire= Frame(frameaffich, bg=col_fond, pady=30)
    frameaffich_taux_horaire.pack(fill=BOTH, expand=True)
        
    frameaffichspe= DoubleScrolledFrame(frameaffich_taux_horaire, borderwidth=2, relief=SUNKEN, bg=col_fond)
    frameaffichspe.canvas.configure(bg=col_fond)
    frameaffichspe.inner.configure(bg=col_fond)
    frameaffichspe.outer.grid(row=0, column=0, sticky="nsew")
    frameaffich_taux_horaire.grid_columnconfigure(0, weight=1)
    frameaffich_taux_horaire.grid_rowconfigure(0, weight=1)
    
    b_ajouter_taux_horaire=Button(frameaffich_taux_horaire, command=ajouter_taux, text="Ajouter un taux horaires", image=pixel, bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_bouton, height=hauteur_bouton, compound="c")
    
    cur=con.cursor()
    t=cur.execute(""" SELECT titre, periodicite_paiement, taux, idth  FROM taux_horaires ORDER BY periodicite_paiement, titre""").fetchall()
    
    labelnom= Label(frameaffichspe, text="Nom du client", bg=col_fond, fg=col_police_basique)
    labelpaiement= Label(frameaffichspe, text="Périodicité de paiement", bg=col_fond, fg=col_police_basique)
    labeltaux= Label(frameaffichspe, text="Montant", bg=col_fond, fg=col_police_basique)
    labelnom.grid(row=0, column=0)
    labelpaiement.grid(row=0, column=1)
    labeltaux.grid(row=0, column=2)
    frameaffichspe.inner.columnconfigure(0, pad=30)
    frameaffichspe.inner.columnconfigure(1, pad=30)
    frameaffichspe.inner.columnconfigure(2, pad=30)
    frameaffichspe.inner.columnconfigure(3, pad=40)
    frameaffichspe.inner.columnconfigure(4, pad=40)
    frameaffichspe.inner.rowconfigure(0, pad=50)
    i=1
    for row in t :
        labelnom= Label(frameaffichspe, text=row[0], bg=col_fond, fg=col_police_basique)
        labelpaiement= Label(frameaffichspe, text=row[1], bg=col_fond, fg=col_police_basique)
        labeltaux= Label(frameaffichspe, text=str(row[2])+" €", bg=col_fond, fg=col_police_basique)
        b_modif_taux_horaire=Button(frameaffichspe, command=lambda row=row : modif_taux(row[3]), text="Modifier", image=pixel, bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_petit_bouton, height=hauteur_petit_bouton, compound="c")
        b_supprimer_taux_horaire=Button(frameaffichspe, command=lambda row=row : supprimer_taux_db(row[3]), text="Supprimer", image=pixel, bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_petit_bouton, height=hauteur_petit_bouton, compound="c")
        labelnom.grid(row=i, column=0)
        labelpaiement.grid(row=i, column=1)
        labeltaux.grid(row=i, column=2)
        b_modif_taux_horaire.grid(row=i, column=3)
        b_supprimer_taux_horaire.grid(row=i, column=4)
        frameaffichspe.inner.rowconfigure(0, pad=15)
        i=i+1

    b_ajouter_taux_horaire.grid(row=i, column=0)
    
    cur.close()
    
    
    
def ajouter_taux() :
    for widget in frameaffich.winfo_children() :
        widget.destroy()
        
    frameaffich_ajouter_taux= Frame(frameaffich, bg=col_fond, pady=30)
    frameaffich_ajouter_taux.pack(fill=BOTH, expand=True)  
    
    frametitre= Frame(frameaffich_ajouter_taux, bg=col_fond, borderwidth=15)
    frameperiodicite= Frame(frameaffich_ajouter_taux, bg=col_fond, borderwidth=15)
    framemontant= Frame(frameaffich_ajouter_taux, bg=col_fond, borderwidth=15) 

    labeltitre=Label(frametitre, text="Nom du'client :", bg=col_fond, fg=col_police_basique)   
    entry_tk_titre=Entry(frametitre, width=40, textvariable=entry_titre)

    labelperiodicite=Label(frameperiodicite, text="Périodicité de paiement :", bg=col_fond, fg=col_police_basique)
    combobox_tk_periodicite = ttk.Combobox(frameperiodicite, values=["horaire", "mensuel"], textvariable=combobx_periodicite)

    labelmontant=Label(framemontant, text="Montant pour une période :", bg=col_fond, fg=col_police_basique)
    entry_tk_montant=Entry(framemontant, width=40, textvariable=entry_montant)

    bajouter_taux_db=Button(frameaffich_ajouter_taux, text="Ajouter", image=pixel, command=ajouter_taux_db, bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_bouton, height=hauteur_bouton, compound="c")
    
       
    for i in range (4) :
        frameaffich_ajouter_taux.grid_rowconfigure(i, weight=1)
        frameaffich_ajouter_taux.rowconfigure(i, pad=20)

    frameaffich_ajouter_taux.grid_columnconfigure(0, weight=1)
    frametitre.grid(row=0, column=0, sticky="nsew")
    framemontant.grid(row=1, column=0, sticky="nsew")
    frameperiodicite.grid(row=2, column=0, sticky="nsew")
    labeltitre.pack()
    entry_tk_titre.pack()
    entry_tk_titre.delete(0, END)
    labelperiodicite.pack()
    combobox_tk_periodicite.pack()
    labelmontant.pack()
    entry_tk_montant.pack()
    entry_tk_montant.delete(0, END)
    bajouter_taux_db.grid(row=3, column=0)
    
def ajouter_taux_db() :
    cur=con.cursor()
    try :
        cur.execute(""" INSERT INTO taux_horaires(titre, periodicite_paiement, taux) VALUES (?,?,?)""", [entry_titre.get(), combobx_periodicite.get(), entry_montant.get()])
        con.commit()
    except sqlite3.Error :
        messagebox.showerror(title="Problème de modification", message="Un problème est survenu lors de l'ajout de ce client")
    cur.close()
    taux_horaire()


def modif_taux(id) :
    for widget in frameaffich.winfo_children() :
        widget.destroy()
    
    cur=con.cursor()
    t=cur.execute(""" SELECT titre, periodicite_paiement, taux FROM taux_horaires WHERE idth=?""", [id]).fetchone()
    cur.close()
    
    frameaffich_modif_taux= Frame(frameaffich, bg=col_fond, pady=30)
    frameaffich_modif_taux.pack(fill=BOTH, expand=True)
    
    frametitre= Frame(frameaffich_modif_taux, bg=col_fond, borderwidth=15)
    frameperiodicite= Frame(frameaffich_modif_taux, bg=col_fond, borderwidth=15)
    framemontant= Frame(frameaffich_modif_taux, bg=col_fond, borderwidth=15) 

    labeltitre=Label(frametitre, text="Nouveau nom du client :", bg=col_fond, fg=col_police_basique)   
    entry_tk_titre=Entry(frametitre, width=40, textvariable=entry_modif_titre)

    labelperiodicite=Label(frameperiodicite, text="Nouvelle périodicité de paiement :", bg=col_fond, fg=col_police_basique)
    combobox_tk_periodicite = ttk.Combobox(frameperiodicite, values=["mensuel", "horaire"], textvariable=combobx_modif_periodicite)

    labelmontant=Label(framemontant, text="Nouveau montant pour une période :", bg=col_fond, fg=col_police_basique)
    entry_tk_montant=Entry(framemontant, width=40, textvariable=entry_modif_montant)

    bmodifier_taux_db=Button(frameaffich_modif_taux, text="Modifier", image=pixel, command=lambda : modifier_taux_db(id), bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_bouton, height=hauteur_bouton, compound="c")
    
       
    for i in range (4) :
        frameaffich_modif_taux.grid_rowconfigure(i, weight=1)
        frameaffich_modif_taux.rowconfigure(i, pad=20)

    frameaffich_modif_taux.grid_columnconfigure(0, weight=1)
    frametitre.grid(row=0, column=0, sticky="nsew")
    framemontant.grid(row=1, column=0, sticky="nsew")
    frameperiodicite.grid(row=2, column=0, sticky="nsew")
    labeltitre.pack()
    entry_tk_titre.pack()
    entry_tk_titre.delete(0, END)
    entry_tk_titre.insert(0, t[0])
    labelperiodicite.pack()
    combobox_tk_periodicite.pack()
    for i in range(len(combobox_tk_periodicite['values'])) :
        if combobox_tk_periodicite['values'][i] == t[1] :
            combobox_tk_periodicite.current(i)                
    labelmontant.pack()
    entry_tk_montant.pack()
    entry_tk_montant.delete(0, END)
    entry_tk_montant.insert(0, t[2])
    bmodifier_taux_db.grid(row=3, column=0)

def modifier_taux_db(id) :
    cur=con.cursor()
    try :
        cur.execute(""" UPDATE taux_horaires SET periodicite_paiement=?, taux= ?, titre=? WHERE idth=?""", [combobx_modif_periodicite.get(), entry_modif_montant.get(), entry_modif_titre.get(), id])
        con.commit()
    except sqlite3.Error :
        messagebox.showerror(title="Problème de modification", message="Un problème est survenu lors de la modification des informations de ce client")
    cur.close()
    taux_horaire()





def supprimer_taux_db(id) :
    cur=con.cursor()
    t=cur.execute(""" SELECT titre FROM taux_horaires WHERE idth=?""", [id]).fetchone()
    if messagebox.askokcancel(title="Suppression", message="Ce processus effacera définitivement les informations concernant "+str(t[0]), icon=messagebox.WARNING)== True :
        
        try :
            cur.execute(""" DELETE FROM taux_horaires WHERE idth=?""", [id])
            con.commit()
        except sqlite3.Error :
            messagebox.showerror(title="Problème de suppression", message="Un problème est survenu lors de la suppression des informations de ce client")

    cur.close()
    taux_horaire()




## Affichage

# Image d'un pixel pour forcer la mesure des widgets en pixel
pixel = PhotoImage(width=1, height=1)

# Fenetre
window.title("MonEntreprise")
window.geometry("1080x720")
window.minsize(1080, 720)
window.config(background=col_fond)
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=2)
window.grid_rowconfigure(2, weight=0)
window.grid_columnconfigure(0, weight=1)

# Frame (div)
framebouton= Frame(window, bg=col_fond, borderwidth=15)
framebouton.grid_rowconfigure(0, weight=1)
framebouton.grid_rowconfigure(1, weight=2)
framebouton.grid_columnconfigure(0, weight=1)

frameaffich= Frame(window, bg=col_fond)


# Titre
lable_title=Label(window, text="MonEntreprise", font=("New York Times", 40), bg=col_fond, fg=col_police_basique)
lable_title.grid(row=0, column=0)


# Boutons
bget_data=Button(framebouton, text="Lire les données du calendrier", image=pixel, command=infos_get_data, bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_bouton, height=hauteur_bouton, compound="c")
btaux_horaire=Button(framebouton, text="Taux horaires", image=pixel, command=taux_horaire, bg=col_bouton, fg=col_police_basique, pady=10, width=longueur_bouton, height=hauteur_bouton, compound="c")


# Afficher
frameaffich.grid(row=1, column=0, sticky="nsew")
framebouton.grid(row=2, column=0, sticky="nsew")
bget_data.grid(row=0, column=0)
btaux_horaire.grid(row=1, column=0)







window.mainloop()
