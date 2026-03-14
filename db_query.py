import sqlite3

# Connexion à la base de données locale
con = sqlite3.connect("MonEntreprise.db")
cur = con.cursor()


#Création de la base de données
cur.execute("""
CREATE TABLE IF NOT EXISTS taux_horaires (
  idth INTEGER PRIMARY KEY AUTOINCREMENT,
  titre TEXT UNIQUE,
  periodicite_paiement TEXT,
  taux SMALLINT);

""")

# cur.execute(""" INSERT INTO taux_horaires(titre, periodicite_paiement, taux) VALUES 
# ('Javier', 'horaire', 30),
# ('Mr DUPONT', 'horaire', 25),
# ('Jaques', 'horaire', 35),
# ('Stéphanie', 'mensuel', 115),
# ('Léa', 'horaire', 30),
# ('Mme Irma', 'mensuel', 95),
# ('Andréa', 'horaire', 25),
# ('Maxime', 'mensuel', 100),
# ('Leila', 'horaire', 25),
# ('Alex', 'horaire', 40)


# """)




t=cur.execute(""" SELECT titre, periodicite_paiement, taux FROM taux_horaires""").fetchall()
for row in t :
  print(str(row)+",")
  
  
# con.commit()

con.close()