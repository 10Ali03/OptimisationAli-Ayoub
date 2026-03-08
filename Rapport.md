# Question 1 — Modélisation du problème et structure du code
1. Modélisation du problème

Le problème étudié est un Vehicle Routing Problem with Time Windows (VRPTW).
Un ensemble de clients doit être desservi par une flotte de véhicules partant et revenant à un dépôt. Chaque client doit être visité exactement une fois, tout en respectant les contraintes de capacité des véhicules et éventuellement des fenêtres de temps. 

Dans un premier temps, le problème est étudié sans tenir compte des fenêtres de temps, ce qui correspond au Capacitated Vehicle Routing Problem (CVRP). Les fenêtres de temps seront ajoutées dans une seconde étape.

Ensembles

V={0,1,…,n}
V={0,1,…,n} : ensemble des sommets du graphe

C={1,…,n}
C={1,…,n} : ensemble des clients

0
0 : dépôt

Paramètres

dij
d
ij
	​

 : distance entre les sommets 
i
i et 
j
j

qi
q
i
	​

 : demande du client 
i
i

Q
Q : capacité maximale d’un véhicule

ai
a
i
	​

 : début de la fenêtre temporelle du client 
i
i

bi
b
i
	​

 : fin de la fenêtre temporelle du client 
i
i

si
s
i
	​

 : durée de service chez le client 
i
i

Variables de décision
xij={1	si un veˊhicule se deˊplace directement de i vers j
0	sinon
x
ij
	​

={
1
0
	​

si un v
e
ˊ
hicule se d
e
ˊ
place directement de i vers j
sinon
	​


Pour la version avec fenêtres de temps :

ti=instant d’arriveˊe au client i
t
i
	​

=instant d’arriv
e
ˊ
e au client i
Fonction objectif

L’objectif est de minimiser la distance totale parcourue par l’ensemble des véhicules.

min⁡∑i∈V∑j∈V,j≠idijxij
min
i∈V
∑
	​

j∈V,j

=i
∑
	​

d
ij
	​

x
ij
	​

Contraintes
1. Chaque client est visité exactement une fois
∑j∈V,j≠ixij=1∀i∈C
j∈V,j

=i
∑
	​

x
ij
	​

=1∀i∈C
∑i∈V,i≠jxij=1∀j∈C
i∈V,i

=j
∑
	​

x
ij
	​

=1∀j∈C
2. Conservation du flot

Si un véhicule arrive chez un client, il doit également en repartir.

∑j∈Vxij=∑j∈Vxji∀i∈C
j∈V
∑
	​

x
ij
	​

=
j∈V
∑
	​

x
ji
	​

∀i∈C
3. Contraintes de capacité

La somme des demandes des clients servis par un véhicule ne doit pas dépasser la capacité maximale 
Q
Q.

4. Fenêtres de temps (dans la seconde phase)

Si un véhicule se déplace de 
i
i vers 
j
j, alors :

tj≥ti+si+dij
t
j
	​

≥t
i
	​

+s
i
	​

+d
ij
	​


et :

ai≤ti≤bi
a
i
	​

≤t
i
	​

≤b
i
	​


Ces contraintes garantissent que les visites respectent les fenêtres temporelles des clients.

2. Structure du code

Afin de faciliter le développement et la lisibilité du projet, le code a été organisé en plusieurs modules distincts.

src/
 ├── main.py
 ├── model.py
 ├── io_utils.py
 ├── evaluate.py
 ├── solver.py
 ├── neighbors.py
 └── meta/
      ├── simulated_annealing.py
      └── tabu_search.py
main.py

Point d’entrée du programme.
Ce module permet de charger les instances, de lancer les algorithmes de résolution et d’afficher les résultats.

model.py

Contient les structures de données principales :

représentation d’un client

représentation d’une instance du problème

représentation d’une solution (ensemble de tournées).

io_utils.py

Module chargé de la lecture des fichiers d’instance et de l’écriture des résultats.

evaluate.py

Contient les fonctions permettant de :

calculer la distance totale d’une solution,

vérifier les contraintes de capacité,

vérifier les fenêtres de temps.

neighbors.py

Implémente les différents opérateurs de voisinage utilisés dans les métaheuristiques :

déplacement d’un client entre deux tournées,

échange de clients,

inversion de segments de tournée (2-opt).

solver.py

Interface principale permettant d’appeler les différentes méthodes de résolution.

meta/

Ce dossier contient les métaheuristiques utilisées dans le projet :

recuit simulé

recherche tabou

# Question 2
Une borne inférieure du nombre de véhicules est donnée par la somme des demandes divisée par la capacité d’un véhicule. Nous testons ensuite si cette borne est atteignable en générant des solutions faisables avec ce nombre de véhicules.