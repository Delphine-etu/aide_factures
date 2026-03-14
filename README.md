# aide_factures
Projet personnel sous Python ayant pour but d'aider des particuliers à établir des factures à partir de taux horaires (grâce à une base de données sqlite) et d'un agenda (à l'aide de l'api google calendar).

Cette application permet, via une interface graphique créée avec la librairie tkinter, d'afficher, créer, modifier et supprimer des données concernant des taux horaires sur une base de données locale sqlite. Il est ainsi possible d'indiquer le nom d'un client, le montant qu'il paie et sa périodicité de paiement.
Il est ensuite possible, toujours via l'interface, d'afficher pour un ou plusieurs mois d'une année donnée, tous les rendez-vous prévus dans cette période par client. Le nombre d'heures et les dates sont affichés par client, ainsi qu'un montant calculé en fonction des informations précédemment entrées en base de données. Un montant et un nombre d'heures total sont également calculés pour l'ensemble des clients de la période.
Cet affichage vise à faciliter le visionnage des informations nécessaires à la création de factures et de déclarations pour les travailleurs indépendants.

L'intégralité du code de ce projet a été écrit par moi-même et sans utilisation d'aucun outil d'Intelligence Artificielle, hormis la classe d'objet "DoubleScrolledFrame" qui provient d'un projet github de novel-yet-trivial (https://gist.github.com/novel-yet-trivial/2841b7b640bba48928200ff979204115).

Les credentials et le token fournis sont issus d'un compte de démonstration lié à des données fictives. Seule la permission "lecture unique" a été accordée depuis ce compte google pour ce projet afin d'éviter toute modification malveillante ou irrespectueuse.
