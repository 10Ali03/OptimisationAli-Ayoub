# VRPTW Project Context — Optimisation Discrète

## 1. Contexte du projet

Ce projet est réalisé dans le cadre du cours d’optimisation discrète.

L’objectif est de résoudre un problème appelé :

Vehicle Routing Problem with Time Windows (VRPTW).

Le problème consiste à organiser les tournées de véhicules partant d’un dépôt afin de servir un ensemble de clients en minimisant la distance totale parcourue.

Chaque client possède :

- une position cartésienne
- une demande
- une fenêtre de temps
- un temps de service

Les véhicules sont identiques et possèdent une capacité maximale.

Chaque client doit être visité exactement une fois.

---

# 2. Objectifs du projet

Le projet comporte plusieurs étapes :

1. Modéliser le problème
2. Structurer le code
3. Déterminer le nombre minimal de véhicules
4. Générer des solutions aléatoires
5. Implémenter deux métaheuristiques
6. Comparer les résultats

Le sujet demande explicitement :

- de commencer sans fenêtres de temps
- puis d'ajouter les fenêtres de temps.

---

# 3. Versions du problème

Deux versions du problème sont étudiées.

## 3.1 Version sans fenêtres de temps

Cette version correspond au problème :

Capacitated Vehicle Routing Problem (CVRP)

Contraintes :

- capacité des véhicules
- chaque client est visité une seule fois
- les tournées commencent et terminent au dépôt

Objectif :

minimiser la distance totale parcourue.

---

## 3.2 Version avec fenêtres de temps

Cette version correspond au problème complet VRPTW.

Contraintes supplémentaires :

Chaque client doit être servi dans sa fenêtre temporelle.

ready_time ≤ arrival_time ≤ due_time

Si le véhicule arrive trop tôt, il doit attendre.

---

# 4. Format des données

Les données sont fournies dans des fichiers `.vrp`.

Exemple :

NAME: data101.vrp  
TYPE: vrptw  
NB_DEPOTS: 1  
NB_CLIENTS: 100  
MAX_QUANTITY: 200  

---

## Dépôt

DATA_DEPOTS

d1 35 35 0 230

Format :

id x y readyTime dueTime

---

## Clients

DATA_CLIENTS

c1 41 49 161 171 10 10

Format :

id x y readyTime dueTime demand service

---

# 5. Modélisation mathématique

## Ensembles

V = {0,...,n}

0 représente le dépôt

C = {1,...,n}

ensemble des clients.

---

## Paramètres

d_ij

distance entre les sommets i et j.

q_i

demande du client i.

Q

capacité maximale d'un véhicule.

[a_i , b_i]

fenêtre de temps du client i.

s_i

temps de service chez le client.

---

## Variables de décision

x_ij = 1 si un véhicule se déplace directement de i vers j  
x_ij = 0 sinon.

---

## Fonction objectif

Minimiser la distance totale parcourue :

min Σ d_ij x_ij

---

## Contraintes

### Visite unique

Chaque client doit être visité exactement une fois.

### Conservation du flot

Si un véhicule arrive chez un client, il doit repartir.

### Capacité

Σ q_i ≤ Q

pour chaque tournée.

### Fenêtres de temps

a_i ≤ t_i ≤ b_i

et

t_j ≥ t_i + s_i + d_ij

---

# 6. Architecture du code

Structure du projet :

src/

main.py  
io_utils.py  
evaluate.py  
construction.py  
solver.py  
neighbors.py  

meta/

simulated_annealing.py  
tabu_search.py  

---

## main.py

Point d’entrée du programme.

Responsabilités :

- charger les instances
- lancer les algorithmes
- afficher les résultats.

---

## io_utils.py

Lecture et parsing des fichiers `.vrp`.

Responsabilités :

- lire les sections du fichier
- créer les objets.

Classes principales :

Depot  
Client  
VRPTWInstance  

---

## evaluate.py

Fonctions d’évaluation :

- distance euclidienne
- distance entre clients
- demande totale
- calcul des bornes inférieures
- calcul de la distance d’une solution
- vérification de faisabilité.

---

## construction.py

Méthodes de construction de solutions.

Fonctions principales :

- construire une solution avec k véhicules
- heuristique gloutonne
- recherche du nombre minimal de véhicules.

---

## neighbors.py

Opérateurs de voisinage utilisés dans les métaheuristiques :

- relocate
- swap
- 2-opt
- échanges inter-routes.

---

## meta/

Contient les métaheuristiques :

simulated_annealing.py  
tabu_search.py  

---

# 7. Question 2 : nombre minimal de véhicules

Pour chaque instance, on cherche :

k_min

le nombre minimal de véhicules nécessaires.

---

## Borne inférieure capacité

Une borne inférieure est donnée par :

LB = ceil( Σ q_i / Q )

où :

Σ q_i est la demande totale  
Q la capacité du véhicule.

Cette borne ne dépend pas :

- des distances
- des fenêtres de temps.

---

# 8. Résultats obtenus sans fenêtres de temps

| Instance | Demande totale | Capacité | LB |
|---------|---------------|---------|----|
| data101 | 1458 | 200 | 8 |
| data102 | 1458 | 200 | 8 |
| data1101 | 1724 | 200 | 9 |
| data1102 | 1724 | 200 | 9 |
| data111 | 1458 | 200 | 8 |
| data112 | 1458 | 200 | 8 |
| data1201 | 1724 | 1000 | 2 |
| data1202 | 1724 | 1000 | 2 |
| data201 | 1458 | 1000 | 2 |
| data202 | 1458 | 1000 | 2 |

Une solution faisable a été trouvée avec exactement cette borne pour toutes les instances.

Donc :

k_min = LB

dans la version sans fenêtres de temps.

---

# 9. Méthode de construction utilisée

Pour tester un nombre de véhicules k :

1. sélectionner k clients graines (les plus éloignés du dépôt)
2. créer k tournées
3. ajouter progressivement les clients les plus proches
4. respecter la capacité
5. vérifier la faisabilité.

Si tous les clients sont servis :

solution faisable trouvée.

Sinon :

tester k+1 véhicules.

---

# 10. Génération de solutions initiales

Le sujet demande un générateur aléatoire.

Principe :

1. ouvrir une nouvelle tournée
2. déterminer les clients admissibles
3. choisir un client aléatoirement
4. l'ajouter à la tournée
5. répéter jusqu'à saturation
6. ouvrir une nouvelle tournée
7. continuer jusqu'à servir tous les clients.

---

# 11. Métaheuristiques prévues

Deux méthodes seront implémentées.

---

## Recuit simulé

Principe :

- exploration probabiliste
- acceptation de solutions moins bonnes
- évitement des minima locaux.

---

## Recherche tabou

Principe :

- mémorisation des mouvements récents
- interdiction temporaire de certains mouvements
- exploration plus large de l'espace des solutions.

---

# 12. Protocole expérimental

Pour chaque instance :

1. générer plusieurs solutions initiales
2. appliquer les métaheuristiques
3. comparer les résultats.

Critères de comparaison :

- distance totale
- temps de calcul
- robustesse.

---

# 13. État actuel du dépôt

Date de référence : 14 mars 2026

Le dépôt contient déjà une première base fonctionnelle pour la version sans fenêtres de temps.

Implémenté actuellement :

- lecture des fichiers `.vrp` dans `src/io_utils.py`
- calcul de la demande totale et de la borne inférieure capacité dans `src/evaluate.py`
- calcul de la distance et de la charge des tournées dans `src/evaluate.py`
- évaluation complète d'une tournée avec temps d'arrivée, attente, début de service et temps de retour
- vérification de faisabilité capacité et fenêtres de temps dans `src/evaluate.py`
- évaluation globale d'une solution avec contrôle "chaque client servi une seule fois"
- construction gloutonne d'une solution capacitaire dans `src/construction.py`
- générateur aléatoire de solutions initiales faisables dans `src/construction.py`
- opérateurs de voisinage `relocate`, `swap` et `2-opt` dans `src/neighbors.py`
- génération et déduplication de voisins faisables dans `src/neighbors.py`
- sélection du meilleur voisin faisable dans `src/neighbors.py`
- génération d'un voisin aléatoire faisable dans `src/neighbors.py`
- première implémentation du recuit simulé dans `src/meta/simulated_annealing.py`
- première implémentation de la recherche tabou dans `src/meta/tabu_search.py`
- protocole expérimental centralisé dans `src/solver.py`
- presets `quick` et `long` pour distinguer validation rapide et tests longs
- mode CLI dédié aux campagnes expérimentales dans `src/main.py`
- recherche du nombre minimal de véhicules à partir de la borne inférieure
- script principal `src/main.py` pour résumer les instances et lancer la recherche

Constat actuel :

- l'exécution de `python3 src/main.py` fonctionne
- une solution faisable est trouvée pour toutes les instances présentes
- les fichiers `src/model.py`, `src/solver.py`, `src/neighbors.py`, `src/meta/simulated_annealing.py` et `src/meta/tabu_search.py` sont encore vides
- la partie fenêtres de temps est maintenant intégrée dans l'évaluation, mais pas encore dans la construction gloutonne
- la génération aléatoire de solutions initiales est implémentée pour la version capacitaire et déjà compatible avec un contrôle temporel
- les voisinages sont maintenant branchés dans une première version du recuit simulé
- la recherche tabou est implémentée dans une première version plus coûteuse en calcul que le recuit simulé
- un cadre de comparaison recuit/tabou existe maintenant, mais les tests longs n'ont pas encore été lancés systématiquement

Résultats observés avec l'état actuel :

| Instance | LB | Véhicules trouvés | Distance |
|---------|----|-------------------|----------|
| data101.vrp | 8 | 8 | 1307.24 |
| data102.vrp | 8 | 8 | 1307.24 |
| data1101.vrp | 9 | 9 | 2093.55 |
| data1102.vrp | 9 | 9 | 2093.55 |
| data111.vrp | 8 | 8 | 1307.24 |
| data112.vrp | 8 | 8 | 1307.24 |
| data1201.vrp | 2 | 2 | 961.46 |
| data1202.vrp | 2 | 2 | 961.46 |
| data201.vrp | 2 | 2 | 929.20 |
| data202.vrp | 2 | 2 | 929.20 |

---

# 14. Suite logique proposée

Ordre recommandé pour la suite du projet :

1. stabiliser le socle d'évaluation d'une solution
2. ajouter les vérifications de faisabilité complètes
3. implémenter un générateur aléatoire de solutions initiales
4. implémenter les voisinages
5. brancher le recuit simulé
6. brancher la recherche tabou
7. ajouter la gestion des fenêtres de temps
8. lancer le protocole expérimental final

Prochaine étape conseillée :

lancer les premiers tests longs contrôlés avec le preset `long` sur un sous-ensemble d'instances, puis consigner précisément les résultats.

Points à brancher ensuite :

- choix du sous-ensemble d'instances pour la première campagne longue
- conservation des tableaux de résultats
- éventuel export CSV ou markdown
- analyse des écarts entre répétitions
- intégration progressive des tableaux dans le rapport

Cela permettra ensuite de lancer les vrais tests longs de comparaison.

---

# 16. Journal de suivi

## 14 mars 2026

Travail réalisé :

- ajout d'un socle d'évaluation complet dans `src/evaluate.py`
- ajout d'une structure `RouteEvaluation`
- centralisation des calculs de distance et de charge
- refactorisation légère de `src/construction.py` pour réutiliser `src/evaluate.py`
- nettoyage de `src/main.py` pour utiliser `solution_distance` depuis `src/evaluate.py`
- implémentation d'un générateur aléatoire de solutions faisables avec nombre de véhicules fixé
- ajout d'un filtre de clients admissibles compatible capacité et fenêtres de temps
- ajout d'un affichage de validation des solutions initiales dans `src/main.py`
- implémentation des voisinages `relocate`, `swap` et `2-opt` dans `src/neighbors.py`
- ajout d'une fonction de génération de voisins faisables et d'une sélection du meilleur voisin
- ajout d'une génération de voisin aléatoire faisable pour éviter un coût trop élevé dans le recuit simulé
- implémentation du recuit simulé avec acceptation probabiliste et suivi de la meilleure solution
- ajout d'un aperçu léger du recuit simulé dans `src/main.py`
- implémentation d'une première recherche tabou avec mémoire tabou sur solutions visitées et aspiration
- ajout d'un aperçu léger de la recherche tabou dans `src/main.py`
- création de `src/solver.py` pour centraliser les expériences
- ajout de presets `quick` et `long` avec paramètres reproductibles
- intégration d'un tableau de comparaison métaheuristiques dans `src/main.py`
- recalibrage du preset `long` pour tenir compte du coût réel de la recherche tabou
- ajout d'une interface de lancement explicite pour les campagnes ciblées (`--mode experiment`)

Vérifications effectuées :

- `python3 src/main.py` exécute toujours correctement le pipeline actuel
- test manuel de `evaluate_route()` sur une tournée simple de `data101.vrp`
- le contrôle des fenêtres de temps détecte bien une tournée non faisable
- génération aléatoire validée sur plusieurs instances avec contrôle de faisabilité global
- test des voisinages sur `data101.vrp` : 9987 voisins faisables générés pour une solution aléatoire testée
- sur cette même solution, un meilleur voisin faisable a été trouvé avec une distance améliorée de 3649.90 à 3512.66
- test ciblé du recuit simulé sur `data101.vrp` : amélioration de 3488.41 à 2211.87 en 500 itérations
- aperçu intégré dans `src/main.py` validé sur 3 instances avec amélioration systématique des solutions initiales
- test ciblé de la recherche tabou sur `data101.vrp` : amélioration de 3604.26 à 3278.86 en 10 itérations
- aperçu intégré de la recherche tabou validé sur `data101.vrp` : amélioration de 3627.92 à 3488.60 en 5 itérations, avec un coût de calcul déjà notable
- protocole `quick` validé sur `data101.vrp` : distance moyenne initiale 3726.26, recuit simulé 2295.29, tabou 3592.33
- sur ce même protocole `quick`, temps moyen observé : 0.10 s pour le recuit simulé contre 12.02 s pour la recherche tabou
- tentative de première campagne `long` : le preset initial s'est révélé trop coûteux pour la recherche tabou
- en conséquence, le preset `long` a été recalibré à un niveau plus réaliste avant de lancer les prochaines campagnes longues
- validation du mode expérimental dédié : `python3 src/main.py --mode experiment --preset quick --instances data101.vrp --details`
- premier test `long` exécuté sur `data101.vrp` avec détail par répétition
- résultat moyen observé sur `data101.vrp` en mode `long` : initial 3719.84, recuit simulé 1800.80, tabou 3424.76
- temps moyens observés sur ce test `long` : 0.36 s pour le recuit simulé contre 19.96 s pour la recherche tabou
- lot `long` exécuté sur `data101.vrp` et `data102.vrp`
- résultat moyen observé sur `data102.vrp` en mode `long` : initial 3609.70, recuit simulé 1764.93, tabou 3372.76
- temps moyens observés sur `data102.vrp` : 0.37 s pour le recuit simulé contre 20.71 s pour la recherche tabou
- lot `long` exécuté sur `data1101.vrp` et `data1102.vrp`
- résultat moyen observé sur `data1101.vrp` en mode `long` : initial 4717.62, recuit simulé 2271.42, tabou 4448.35
- résultat moyen observé sur `data1102.vrp` en mode `long` : initial 4683.40, recuit simulé 2368.66, tabou 4311.87
- temps moyens observés sur `data1101.vrp` et `data1102.vrp` : environ 0.48 s pour le recuit simulé contre environ 20.3 s pour la recherche tabou
- lot `long` exécuté sur `data111.vrp` et `data112.vrp`
- résultats observés sur `data111.vrp` et `data112.vrp` identiques à ceux de `data101.vrp` et `data102.vrp` avec les mêmes graines
- cette répétition suggère fortement que ces paires d'instances partagent la même structure utile pour nos heuristiques actuelles
- lot `long` exécuté sur `data1201.vrp` et `data1202.vrp`
- résultat moyen observé sur `data1201.vrp` en mode `long` : initial 4507.39, recuit simulé 1898.40, tabou 4191.42
- résultat moyen observé sur `data1202.vrp` en mode `long` : initial 4693.59, recuit simulé 2051.32, tabou 4216.21
- sur ces instances à 2 véhicules, le recuit simulé reste très performant et encore plus rapide, autour de 0.26 s
- lot `long` exécuté sur `data201.vrp` et `data202.vrp`
- résultat moyen observé sur `data201.vrp` en mode `long` : initial 3410.18, recuit simulé 1547.01, tabou 3111.51
- résultat moyen observé sur `data202.vrp` en mode `long` : initial 3436.16, recuit simulé 1660.53, tabou 3129.50
- la première campagne longue couvre maintenant toutes les familles d'instances présentes dans le dépôt
- un tableau récapitulatif complet de la première campagne longue a été ajouté dans `rapport.tex`
- intégration d'une heuristique d'insertion pour la construction avec fenêtres de temps dans `src/construction.py`
- recherche du nombre minimal de véhicules avec fenêtres de temps maintenant branchée dans `src/main.py`
- premiers résultats VRPTW observés : `data101.vrp -> 21`, `data102.vrp -> 18`, `data1101.vrp -> 18`, `data1201.vrp -> 5`, `data201.vrp -> 5`
- constat VRPTW actuel : la construction déterministe par insertion fonctionne, mais le générateur aléatoire avec fenêtres de temps ne trouve pas encore facilement de solution faisable
- fallback déterministe ajouté dans les métaheuristiques pour permettre des essais VRPTW malgré la fragilité du générateur aléatoire
- test VRPTW ciblé validé : sur `data1201.vrp`, recuit simulé exécuté à partir d'une solution faisable avec `k=5`, faisabilité conservée
- campagnes expérimentales maintenant persistées dans `experiment_results.log` après chaque instance terminée
- idée validée : on pourra interrompre un test long et relire les résultats partiels au prompt suivant
- première expérience VRPTW `quick` complète validée sur `data1201.vrp`
- résultat observé sur `data1201.vrp` avec fenêtres de temps : initial 1974.63, recuit simulé 1909.98, tabou 1945.36
- temps observés en VRPTW `quick` sur `data1201.vrp` : 0.74 s pour le recuit simulé et 9.35 s pour la recherche tabou
- campagne VRPTW `quick` sur les 10 instances terminée et persistée dans `experiment_results.log`
- résultats VRPTW `quick` désormais disponibles pour tout le corpus, avec `k` faisable, distance initiale, recuit simulé et recherche tabou pour chaque instance
- campagne VRPTW `quick` complète intégrée dans `rapport.tex` avec tableau récapitulatif et analyse

---

# 15. Règle de suivi de collaboration

À partir de maintenant, `codex.md` sert aussi de mémoire de travail, et `rapport.tex` doit être mis à jour au fur et à mesure pour refléter l'avancement réel du projet.

Le rapport doit aussi expliquer l'évolution du code et des choix d'architecture : pourquoi certains modules ont été séparés, pourquoi certaines refactorisations ont été faites, et quelle logique a guidé le découpage en fichiers.

Les astuces d'organisation interne pour les tests longs (par exemple les fichiers de log temporaires) ne doivent pas apparaître dans le rapport final. Elles servent uniquement à sécuriser notre travail et à mieux noter les résultats pendant le projet.

Procédure pour les futurs chats :

- avant de relancer une campagne longue, relire d'abord `experiment_results.log`
- considérer ce fichier comme la source de vérité pour savoir quelles instances ont déjà été calculées
- si une campagne a été interrompue, reprendre à partir des instances non encore présentes dans le log
- recopier ensuite seulement les résultats utiles dans `codex.md` et `rapport.tex`
- supprimer les fichiers de log temporaires à la fin du projet

À chaque modification importante, on mettra à jour :

- ce qui a été implémenté
- ce qui reste à faire
- les hypothèses retenues
- les résultats observés après test
- les sections du rapport qui doivent être synchronisées

Objectif :

garder un historique clair du projet, de ses choix techniques et de l'avancement.

---

# 16. Mise à jour du 2026-03-14

- ajout d'un suivi explicite du nombre de voisins traités par les métaheuristiques
- `src/meta/simulated_annealing.py` compte maintenant les voisins faisables générés
- `src/meta/tabu_search.py` exposait déjà le nombre de voisins explorés ; ces métriques sont maintenant résumées dans `src/solver.py`
- `src/main.py --mode experiment` affiche désormais aussi un tableau `Voisins générés/explorés`
- validation sur `data101.vrp` en mode `quick` :
  - recuit simulé : `300` voisins générés en moyenne, `141` mouvements acceptés
  - recherche tabou : `200` voisins explorés, `5` mouvements acceptés

- ajout du bonus exact dans `src/bonus_exact.py` et branchement dans `src/main.py --mode bonus`
- commande type :
  - `python3 src/main.py --mode bonus --instances data101.vrp --sizes 5 10 15 20 25 30 35 40 --time-limit 10`
- résultats bonus actuels sur `data101.vrp` :
  - `5` clients : `OPTIMAL`, `0.03 s`
  - `10` clients : `OPTIMAL`, `0.01 s`
  - `15` clients : `OPTIMAL`, `0.74 s`
  - `20` clients : `OPTIMAL`, `0.46 s`
  - `25` clients : `OPTIMAL`, `5.08 s`
  - `30` clients : `FEASIBLE` à la limite de `10 s`
  - `35` clients : `FEASIBLE` à la limite de `10 s`
  - `40` clients : `FEASIBLE` à la limite de `10 s`
- lecture actuelle : dans notre configuration, la résolution exacte devient déjà sensiblement difficile autour de `30` clients

- campagne VRPTW `long` terminée sur les 10 instances (log définitif : `tmp/experiments/final_long_vrptw.log`)
- résultats finaux (valeurs moyennées sur 2 répétitions — source de vérité = log) :
  - `data101.vrp`  : k=21, initial `2127.09`, recuit `1756.06`, tabou `1852.75`, temps RS `25.00`s, temps tabou `60.23`s
  - `data102.vrp`  : k=18, initial `1794.68`, recuit `1683.80`, tabou `1610.82`, temps RS `5.64`s, temps tabou `18.55`s
  - `data1101.vrp` : k=18, initial `2184.86`, recuit `1851.01`, tabou `1864.19`, temps RS `9.01`s, temps tabou `41.16`s
  - `data1102.vrp` : k=16, initial `1913.17`, recuit `1753.92`, tabou `1663.26`, temps RS `6.19`s, temps tabou `12.62`s
  - `data111.vrp`  : k=14, initial `1601.37`, recuit `1426.25`, tabou `1417.19`, temps RS `4.26`s, temps tabou `11.74`s
  - `data112.vrp`  : k=12, initial `1434.70`, recuit `1256.10`, tabou `1229.63`, temps RS `5.15`s, temps tabou `9.49`s
  - `data1201.vrp` : k=5,  initial `2267.76`, recuit `1840.63`, tabou `1752.22`, temps RS `4.13`s, temps tabou `9.85`s
  - `data1202.vrp` : k=4,  initial `1924.75`, recuit `1700.61`, tabou `1633.87`, temps RS `3.36`s, temps tabou `7.06`s
  - `data201.vrp`  : k=5,  initial `1759.27`, recuit `1631.38`, tabou `1449.18`, temps RS `3.10`s, temps tabou `6.86`s
  - `data202.vrp`  : k=5,  initial `1506.60`, recuit `1506.60`, tabou `1282.73`, temps RS `1.61`s, temps tabou `2.94`s
- lecture actuelle :
  - en VRPTW `long`, la tabou est meilleure sur la majorité des instances (data102, data1102, data111, data112, data1201, data1202, data201, data202)
  - le recuit simulé reste meilleur sur data101 (k=21) et légèrement sur data1101
  - cas atypique data202 : recuit ne parvient pas à améliorer l'initiale (1506.60 → 1506.60), la tabou descend à 1282.73
  - la tabou est plus coûteuse en temps mais reste acceptable sauf data101 (~60s pour 2 répétitions)
- `rapport.tex` mis à jour : table VRPTW long corrigée avec ces temps de référence
- pour reprendre dans un futur chat :
  - lire d'abord `tmp/experiments/vrptw_long.log`
  - considérer le log comme source de vérité
  - ne reporter dans `rapport.tex` que des résultats terminés et stables

# 17. Mise à jour du 2026-04-12

Corrections apportées lors de cette session :

- **bug corrigé dans `src/meta/simulated_annealing.py`** : les fonctions `lower_bound_vehicles` et `build_solution_with_k_vehicles` étaient utilisées dans la branche de fallback VRPTW (lignes 49–54) sans être importées. Cela aurait causé un `NameError` si `generate_random_solution` renvoyait `None` sur une instance VRPTW difficile. Les imports ont été ajoutés (`from construction import build_solution_with_k_vehicles, generate_random_solution` et `from evaluate import evaluate_solution, lower_bound_vehicles`).
- **rapport.tex mis à jour** : la table de résultats VRPTW en mode `long` avait des temps légèrement différents des valeurs du log de référence (`final_long_vrptw.log`). Les temps ont été corrigés pour correspondre exactement au log.
- **contexte.md mis à jour** : les résultats VRPTW `long` de la section 16 (journal 14 mars 2026) étaient issus d'une version antérieure de la tabou ; ils ont été remplacés par les valeurs finales du log.

- **`src/main.py` corrigé** : l'import de `bonus_exact` (qui requiert `ortools`) était fait au niveau module. Si `ortools` n'est pas installé, toute la commande échouait, y compris les modes `experiment` et `overview`. L'import est maintenant conditionnel (uniquement au moment où `--mode bonus` est demandé).

Campagne de validation CVRP `long` relancée et terminée dans `tmp/experiments/fresh_long_cvrp.log`.

Résultats frais CVRP `long` (12 avril 2026) — distances confirment le log de référence, la tabou est parfaitement reproductible (déterministe), la SA varie légèrement (stochastique) :

| Instance | k | Init moy | SA moy | Tabou moy | Temps SA | Temps tabou |
|---|---|---|---|---|---|---|
| data101.vrp  | 8 | 3719.84 | 1800.80 | 2419.86 | 0.54 | 0.85 |
| data102.vrp  | 8 | 3609.70 | 1764.93 | 2389.28 | 0.53 | 0.84 |
| data1101.vrp | 9 | 4801.67 | 2237.07 | 3202.56 | 0.63 | 1.05 |
| data1102.vrp | 9 | 4702.59 | 2455.44 | 3063.83 | 0.66 | 1.09 |
| data111.vrp  | 8 | 3480.20 | 1716.46 | 2306.55 | 0.50 | 0.95 |
| data112.vrp  | 8 | 3550.56 | 1819.29 | 2317.44 | 0.56 | 0.86 |
| data1201.vrp | 2 | 4584.95 | 2001.83 | 2905.82 | 0.51 | 0.69 |
| data1202.vrp | 2 | 4458.85 | 2009.33 | 2844.22 | 0.37 | 0.59 |
| data201.vrp  | 2 | 3324.19 | 1669.67 | 2147.25 | 0.36 | 0.60 |
| data202.vrp  | 2 | 3401.22 | 1611.37 | 2219.52 | 0.35 | 0.59 |

Campagne VRPTW `long` : non relancée dans le sandbox (la phase `find_minimum_vehicles` avec fenêtres de temps pour data101 passe de k=8 à k=21 via des insertions O(n³) sur 100 clients, trop lent sans votre machine). Le log de référence `final_long_vrptw.log` reste la source de vérité pour les résultats VRPTW.

---

# 19. Mise à jour du 2026-04-12 (session 2)

## Bug de performance corrigé dans `src/solver.py`

`generate_random_solution` était appelée avec `max_attempts=100` pour le VRPTW.
Or les tentatives aléatoires échouent toutes systématiquement pour les instances VRPTW
(contraintes temporelles trop restrictives) : chaque tentative coûtait ~1.7 s × 100 = ~170 s
gaspillées par run, avant que le safety net déterministe (2.5 s, toujours faisable) ne prenne le relais.

Correction appliquée dans `run_metaheuristics_on_instance` :

```python
_max_attempts = 3 if check_time_windows else 100
initial_routes = generate_random_solution(
    instance,
    k=found_k,
    max_attempts=_max_attempts,
    ...
)
```

Gain : la construction initiale VRPTW passe de ~170 s à ~10 s par appel. La qualité des
résultats est identique (le safety net est deterministe, il retourne toujours la même solution).

## Campagne VRPTW `long` re-lancée et terminée (valeurs de référence)

Durée totale : 13 min 58 s pour les 10 instances × 2 répétitions.
Fichier de référence : `tmp/experiments/fresh_long_vrptw.log`

| Instance | k | Init moy | SA moy | Tabou moy | Temps SA | Temps tabou |
|---|---|---|---|---|---|---|
| data101.vrp  | 21 | 2127.09 | 1756.06 | 1852.75 | 22.26 | 52.34 |
| data102.vrp  | 18 | 1794.68 | 1683.80 | 1610.82 | 5.15  | 16.97 |
| data1101.vrp | 18 | 2184.86 | 1851.01 | 1864.19 | 8.25  | 35.73 |
| data1102.vrp | 16 | 2035.58 | 1765.05 | 1756.30 | 5.46  | 14.73 |
| data111.vrp  | 14 | 1601.37 | 1426.25 | 1417.19 | 3.71  | 10.24 |
| data112.vrp  | 12 | 1434.70 | 1256.10 | 1229.63 | 4.53  | 8.83  |
| data1201.vrp | 5  | 2106.72 | 1815.58 | 1696.96 | 3.89  | 10.02 |
| data1202.vrp | 4  | 1948.06 | 1746.99 | 1648.81 | 3.02  | 6.86  |
| data201.vrp  | 5  | 1759.27 | 1631.38 | 1449.18 | 3.02  | 6.71  |
| data202.vrp  | 5  | 1506.60 | 1506.60 | 1282.73 | 1.53  | 2.88  |

Différences vs session précédente (section 16) :
- data1102 : init légèrement différente (2035.58 vs 1913.17), tabou légèrement moins bonne (1756.30 vs 1663.26)
- data1201 : init différente (2106.72 vs 2267.76), RS et tabou légèrement améliorés
- data1202 : init légèrement différente, RS et tabou légèrement différents
- Tous les temps sont plus courts grâce au bug fix (plus de 170 s gaspillées en construction)
- Les tendances globales sont identiques : tabou meilleure sur 7/10 instances VRPTW

## `rapport.tex` mis à jour

- Table VRPTW `long` (section "Campagne VRPTW en mode long") corrigée avec les nouvelles valeurs
- Référence textuelle à `(1752.22 contre 1840.63)` mise à jour en `(1696.96 contre 1815.58)` pour data1201
- `experiment_results.log` consolidé avec CVRP long + VRPTW long (20 instances, 126 lignes)

---

# 18. État réel pour le prochain chat

Questions du sujet maintenant couvertes :

- modélisation du problème : oui
- structure du code : oui
- nombre minimal de véhicules sans fenêtres de temps : oui
- nombre minimal de véhicules avec fenêtres de temps : oui
- générateur aléatoire de solutions sans fenêtres de temps : oui
- générateur aléatoire de solutions avec fenêtres de temps : partiellement seulement, encore fragile
- deux métaheuristiques implémentées : oui
- protocole expérimental expliqué : oui
- comparaison temps / qualité / nombre de voisins traités / paramètres : oui
- bonus exact avec solveur linéaire : oui, première étude faite avec OR-Tools

État du rapport :

- `rapport.tex` est globalement à jour par rapport au code
- la campagne CVRP `long` complète est intégrée
- la campagne VRPTW `quick` complète est intégrée
- la campagne VRPTW `long` complète est intégrée
- le bonus exact est intégré
- le rapport ne doit toujours pas mentionner nos outils internes de log ou notre organisation de suivi

Ce qu'il reste vraiment à faire :

- éventuellement améliorer le générateur aléatoire VRPTW pour qu'il soit robuste, et pas seulement remplacé par un fallback déterministe
- éventuellement améliorer la recherche tabou, qui reste en retrait par rapport au recuit simulé
- faire le nettoyage final du dépôt avant rendu

Procédure de reprise recommandée :

- relire d'abord `codex.md`
- relire ensuite `tmp/experiments/vrptw_long.log` et `experiment_results.log` si on reprend un travail expérimental
- considérer les logs comme source de vérité brute
- ne recopier dans `rapport.tex` que des résultats stabilisés
- garder les fichiers temporaires dans `tmp/` jusqu'à la toute fin, puis les supprimer avant rendu si nécessaire

Lecture synthétique actuelle (source : `final_long_cvrp.log` et `final_long_vrptw.log`) :

- sans fenêtres de temps (CVRP), le recuit simulé domine très nettement la recherche tabou en qualité et en temps
- avec fenêtres de temps (VRPTW), la recherche tabou devient meilleure sur la majorité des instances ; le recuit simulé reste meilleur seulement sur les cas les plus contraints (data101, data1101)
- la recherche tabou est plus coûteuse en temps, surtout en VRPTW
- les fenêtres de temps augmentent fortement le nombre de véhicules nécessaires
- l'étude exacte avec OR-Tools devient déjà plus difficile autour de `30` clients dans notre cadre expérimental
# 18. Mise Ã  jour du 2026-03-20

- l'environnement Python a Ã©tÃ© rÃ©parÃ© via Python Manager
- `ortools` a Ã©tÃ© installÃ© dans cet environnement pour permettre l'exÃ©cution de `src/main.py`
- validation de reprise effectuÃ©e sur `data101.vrp` en mode `quick`
- relance complÃ¨te des campagnes `long` CVRP et VRPTW sur les 10 instances

RÃ©sultats CVRP `long` observÃ©s sur cette relance :

- `data101.vrp` : initial `3719.84`, recuit `1814.38`, tabou `3424.76`
- `data102.vrp` : initial `3609.70`, recuit `1765.58`, tabou `3372.76`
- `data1101.vrp` : initial `4801.67`, recuit `2322.33`, tabou `4411.14`
- `data1102.vrp` : initial `4702.59`, recuit `2455.44`, tabou `4427.25`
- `data111.vrp` : initial `3480.20`, recuit `1700.26`, tabou `3180.53`
- `data112.vrp` : initial `3550.56`, recuit `1738.23`, tabou `3229.16`
- `data1201.vrp` : initial `4584.95`, recuit `2001.83`, tabou `4100.91`
- `data1202.vrp` : initial `4458.85`, recuit `2009.33`, tabou `4042.31`
- `data201.vrp` : initial `3324.19`, recuit `1669.67`, tabou `3035.40`
- `data202.vrp` : initial `3401.22`, recuit `1611.37`, tabou `3118.30`

Temps moyens CVRP `long` observÃ©s sur cette relance :

- recuit simulÃ© : environ `0.34 s` Ã  `1.31 s`
- recherche tabou : environ `23.67 s` Ã  `36.56 s`
- voisins moyens traitÃ©s :
  - recuit simulÃ© : `1200`
  - recherche tabou : `600`

RÃ©sultats VRPTW `long` observÃ©s sur cette relance :

- `data101.vrp` : initial `2127.09`, recuit `1756.06`, tabou `2042.71`
- `data102.vrp` : initial `1794.68`, recuit `1683.80`, tabou `1695.11`
- `data1101.vrp` : initial `2184.86`, recuit `1851.01`, tabou `2036.87`
- `data1102.vrp` : initial `2035.58`, recuit `1765.05`, tabou `1955.24`
- `data111.vrp` : initial `1601.37`, recuit `1426.25`, tabou `1557.55`
- `data112.vrp` : initial `1434.70`, recuit `1256.10`, tabou `1367.21`
- `data1201.vrp` : initial `1974.63`, recuit `1833.03`, tabou `1864.35`
- `data1202.vrp` : initial `1948.06`, recuit `1746.99`, tabou `1861.51`
- `data201.vrp` : initial `2263.65`, recuit `1656.57`, tabou `2074.35`
- `data202.vrp` : initial `2997.76`, recuit `1772.69`, tabou `2797.17`

Temps moyens VRPTW `long` observÃ©s sur cette relance :

- recuit simulÃ© : environ `1.81 s` Ã  `28.38 s`
- recherche tabou : environ `22.98 s` Ã  `40.71 s`
- voisins moyens traitÃ©s :
  - recuit simulÃ© : `1200` sur presque toutes les instances, `1162` sur `data101.vrp`
  - recherche tabou : `600`

Lecture actuelle aprÃ¨s relance :

- les conclusions de fond ne changent pas : le recuit simulÃ© reste la meilleure mÃ©taheuristique du projet dans notre implÃ©mentation actuelle
- la recherche tabou reste dominÃ©e en qualitÃ© et plus coÃ»teuse en temps, en CVRP comme en VRPTW
- les temps absolus de cette relance sont plus Ã©levÃ©s que ceux notÃ©s plus tÃ´t dans le projet, mais l'ordre relatif des mÃ©thodes reste inchangÃ©
- `rapport.tex` doit maintenant reflÃ©ter cette relance rÃ©cente plutÃ´t que les anciennes mesures de temps

Questions du sujet couvertes aprÃ¨s cette relance :

- modÃ©lisation : oui
- architecture du code : oui
- nombre minimal de vÃ©hicules sans fenÃªtres de temps : oui
- nombre minimal de vÃ©hicules avec fenÃªtres de temps : oui
- gÃ©nÃ©ration initiale sans fenÃªtres de temps : oui
- gÃ©nÃ©ration initiale avec fenÃªtres de temps : encore partielle, avec fallback dÃ©terministe si besoin
- deux mÃ©taheuristiques : oui
- protocole expÃ©rimental complet : oui
- comparaison qualitÃ© / temps / voisins traitÃ©s : oui
- bonus exact avec OR-Tools : oui

Ce qu'il reste rÃ©ellement Ã  faire :

- amÃ©liorer si on le souhaite la robustesse du gÃ©nÃ©rateur alÃ©atoire VRPTW
- amÃ©liorer si on le souhaite la recherche tabou
- faire le nettoyage final du dÃ©pÃ´t et une derniÃ¨re relecture du rapport avant rendu
---

# 19. Mise Ã  jour finale du 2026-03-20

- optimisation de `src/evaluate.py` avec cache des distances et Ã©valuation de route en un seul passage
- amÃ©lioration de l'initialisation alÃ©atoire VRPTW dans `src/construction.py` par insertion alÃ©atoire guidÃ©e
- ajout d'un Ã©chantillonnage bornÃ© de voisins dans `src/neighbors.py`
- recherche tabou mise Ã  jour pour exploiter cet Ã©chantillonnage dans `src/meta/tabu_search.py`
- preset `long` recalibrÃ© dans `src/solver.py` :
  - tabou `20` itÃ©rations
  - tenure `12`
  - `100` voisins max par itÃ©ration

Campagne finale CVRP `long` aprÃ¨s amÃ©liorations :

- `data101.vrp` : initial `3719.84`, recuit `1814.38`, tabou `2419.86`
- `data102.vrp` : initial `3609.70`, recuit `1765.58`, tabou `2389.28`
- `data1101.vrp` : initial `4801.67`, recuit `2322.33`, tabou `3202.56`
- `data1102.vrp` : initial `4702.59`, recuit `2455.44`, tabou `3063.83`
- `data111.vrp` : initial `3480.20`, recuit `1700.26`, tabou `2306.55`
- `data112.vrp` : initial `3550.56`, recuit `1738.23`, tabou `2317.44`
- `data1201.vrp` : initial `4584.95`, recuit `2001.83`, tabou `2905.82`
- `data1202.vrp` : initial `4458.85`, recuit `2009.33`, tabou `2844.22`
- `data201.vrp` : initial `3324.19`, recuit `1669.67`, tabou `2147.25`
- `data202.vrp` : initial `3401.22`, recuit `1611.37`, tabou `2219.52`

Lecture CVRP actuelle :

- le recuit simulÃ© reste clairement la meilleure mÃ©thode en qualitÃ©
- la recherche tabou a Ã©tÃ© trÃ¨s fortement amÃ©liorÃ©e
- la recherche tabou n'est plus du tout prohibitive en temps :
  - environ `0.52 s` Ã  `2.75 s`
  - contre des dizaines de secondes auparavant

Campagne finale VRPTW `long` aprÃ¨s amÃ©liorations :

- `data101.vrp` : initial `2127.09`, recuit `1756.06`, tabou `1852.75`
- `data102.vrp` : initial `1794.68`, recuit `1683.80`, tabou `1610.82`
- `data1101.vrp` : initial `2184.86`, recuit `1851.01`, tabou `1864.19`
- `data1102.vrp` : initial `1913.17`, recuit `1753.92`, tabou `1663.26`
- `data111.vrp` : initial `1601.37`, recuit `1426.25`, tabou `1417.19`
- `data112.vrp` : initial `1434.70`, recuit `1256.10`, tabou `1229.63`
- `data1201.vrp` : initial `2267.76`, recuit `1840.63`, tabou `1752.22`
- `data1202.vrp` : initial `1924.75`, recuit `1700.61`, tabou `1633.87`
- `data201.vrp` : initial `1759.27`, recuit `1631.38`, tabou `1449.18`
- `data202.vrp` : initial `1506.60`, recuit `1506.60`, tabou `1282.73`

Lecture VRPTW actuelle :

- la recherche tabou recalibrÃ©e devient meilleure que le recuit simulÃ© sur `8` instances sur `10`
- le recuit simulÃ© garde un avantage net sur `data101.vrp`
- le recuit simulÃ© reste trÃ¨s proche de la tabou sur `data1101.vrp`
- la recherche tabou coÃ»te plus cher sur quelques gros cas VRPTW, surtout `data101.vrp`, mais reste raisonnable sur le reste du corpus

Questions du sujet : Ã©tat actuel

- modÃ©lisation : oui
- structure du code : oui
- nombre minimal de vÃ©hicules sans fenÃªtres de temps : oui
- nombre minimal de vÃ©hicules avec fenÃªtres de temps : oui
- gÃ©nÃ©rateur alÃ©atoire sans fenÃªtres de temps : oui
- gÃ©nÃ©rateur alÃ©atoire avec fenÃªtres de temps : mieux qu'avant, mais encore pas entiÃ¨rement robuste
- deux mÃ©taheuristiques : oui
- protocole expÃ©rimental complet : oui
- comparaison qualitÃ© / temps / voisins traitÃ©s : oui
- bonus exact OR-Tools : oui

Ce qu'il reste vraiment Ã  faire maintenant :

- finaliser si on le souhaite la robustesse complÃ¨te du gÃ©nÃ©rateur alÃ©atoire VRPTW
- Ã©ventuellement affiner encore la tabou sur les cas extrÃªmes comme `data101.vrp`
- faire la relecture finale du rapport
- nettoyer le dÃ©pÃ´t avant rendu
---

# 20. Nettoyage et compilation du 2026-03-20

- suppression des `__pycache__` Python du dÃ©pÃ´t
- suppression des anciens logs temporaires dans `tmp/experiments`
- suppression des anciens fichiers auxiliaires LaTeX dans `tmp/latex`
- relecture ciblÃ©e de `rapport.tex` pour aligner les conclusions avec la campagne finale amÃ©liorÃ©e
- compilation du rapport avec `pdflatex` en deux passes via MiKTeX
- copie du PDF compilÃ© vers `rapport.pdf` Ã  la racine du projet

Ã‰tat final de compilation :

- `rapport.pdf` recompilÃ© avec succÃ¨s
- quelques avertissements LaTeX mineurs subsistent :
  - quelques `Overfull \hbox`
  - un avertissement `hyperref` sur une chaÃ®ne PDF contenant du mode math
  - un avertissement de duplication d'identifiant de page liÃ© au dÃ©but du document
- ces avertissements n'empÃªchent pas la production du PDF

Ce qu'il reste vraiment avant rendu :

- relire visuellement `rapport.pdf`
- dÃ©cider si l'on veut corriger aussi les petits avertissements LaTeX restants ou s'arrÃªter lÃ 
- vÃ©rifier une derniÃ¨re fois les noms / auteurs rÃ©els sur la page de garde du rapport
# 21. Mise à jour rapport final du 2026-03-20

- relecture approfondie de `rapport.tex` pour renforcer la cohérence avec le code final et les logs `final_long_*`
- modélisation mathématique rendue plus rigoureuse :
  - domaines des variables ajoutés
  - contrainte temporelle formulée avec grand `M`
  - ajout d'une remarque sur la formulation PLNE complète possible et l'élimination des sous-tournées
- clarification du lien entre modèle théorique et choix d'implémentation :
  - capacité contrôlée dans l'évaluation de route
  - faisabilité temporelle contrôlée dans l'évaluation de route
- renforcement de la question 2 :
  - meilleure mise en avant du fait que la borne capacité est atteinte sur tout le corpus CVRP étudié
  - ajout d'une nuance explicite : ce constat vaut pour notre corpus et ne constitue pas une propriété générale du CVRP
  - ajout d'un tableau synthétique `LB capacité / k minimal CVRP / k minimal VRPTW`
- générateur aléatoire :
  - rapport clarifié pour indiquer que la génération aléatoire répond pleinement au besoin en CVRP
  - en VRPTW, la robustesse reste partielle et un fallback déterministe est utilisé
  - formulation défensive ajoutée pour bien couvrir la consigne du sujet sans contredire le code réel
- métaheuristiques :
  - tableau synthétique des paramètres `quick` et `long` ajouté
  - sous-section sur les critères de comparaison ajoutée
  - sous-section sur la reproductibilité et les répétitions ajoutée
  - pseudo-code simplifié du recuit simulé ajouté dans le rapport
- protocole expérimental :
  - ajout d'indicateurs de dispersion min / max / écart-type sur quelques cas représentatifs
  - conclusions expérimentales resserrées pour distinguer clairement CVRP et VRPTW

Figures désormais intégrées dans `rapport.tex` et `rapport.pdf` :

- `figures/comparison_vehicles.png` :
  - impact des fenêtres de temps sur le nombre minimal de véhicules
- `figures/convergence_data101_cvrp.png` :
  - courbe de convergence en CVRP sur `data101.vrp`
- `figures/convergence_data1201_vrptw.png` :
  - courbe de convergence en VRPTW sur `data1201.vrp`
- `figures/comparison_distances.png` :
  - comparaison des distances finales sur les campagnes longues CVRP et VRPTW
- `figures/comparison_times.png` :
  - comparaison des temps d'exécution sur les campagnes longues CVRP et VRPTW
- `figures/routes_data1201_comparison.png` :
  - visualisation comparative de tournées sur `data1201.vrp` en CVRP et VRPTW

Source réelle des nouvelles figures :

- les graphes agrégés sont construits à partir des résultats finaux présents dans :
  - `tmp/experiments/final_long_cvrp.log`
  - `tmp/experiments/final_long_vrptw.log`
- les visualisations de tournées et les courbes de convergence sont reconstruites à partir du code final et de graines contrôlées :
  - convergence CVRP sur `data101.vrp`
  - convergence VRPTW sur `data1201.vrp`
  - visualisation de tournées sur `data1201.vrp`

Lecture finale actuelle du rapport :

- en CVRP :
  - la borne capacité est atteinte sur tout le corpus étudié
  - le recuit simulé reste le meilleur compromis qualité / temps
- en VRPTW :
  - les fenêtres de temps augmentent fortement le nombre de véhicules nécessaires
  - la recherche tabou recalibrée devient globalement meilleure sur la campagne longue finale
  - le générateur aléatoire reste moins robuste que dans le cas capacitaire

État réel en fin de chat :

- `rapport.tex` : mis à jour et cohérent avec le code final
- `rapport.pdf` : recompilé avec succès après chaque série de modifications
- avertissements LaTeX mineurs toujours présents :
  - quelques `Overfull \hbox`
  - un avertissement `hyperref` lié à du mode math dans une chaîne PDF
  - un avertissement de duplication d'identifiant de page au début du document
- ces avertissements n'empêchent pas la production du PDF

Ce qu'il reste vraiment avant rendu :

- remplacer les noms factices de la page de garde par les vrais noms
- relire visuellement `rapport.pdf`
- décider si l'on corrige ou non les avertissements LaTeX restants

# 22. Décision sur l'analyse du corpus du 2026-03-20

- clarification méthodologique ajoutée au rapport :
  - les conclusions finales ne reposent pas sur quelques exemples isolés
  - elles reposent sur l'ensemble du corpus final de `10` instances en CVRP et en VRPTW
- choix rédactionnel retenu :
  - conserver une analyse synthétique sur tout le corpus dans le corps du rapport
  - commenter seulement quelques cas représentatifs ou atypiques pour éviter un catalogue instance par instance
- cas explicitement retenus comme études de cas utiles :
  - `data101.vrp` :
    - cas VRPTW le plus contraint du corpus
    - utile pour montrer le coût des contraintes temporelles sévères
  - `data1201.vrp` :
    - cas charnière pour illustrer le basculement CVRP vers VRPTW
    - déjà utilisé pour la visualisation de tournées
  - `data202.vrp` :
    - cas atypique en VRPTW où le recuit simulé améliore peu ou pas la solution initiale moyenne
    - utile pour justifier l'intérêt d'une exploration tabou plus structurée
- conséquence sur le rapport :
  - renforcement du message "analyse globale + cas marquants"
  - conclusion resserrée pour rappeler que les études de cas servent d'interprétation et non de base statistique unique

---

# 23. Mise à jour du 2026-04-30

## Diagnostic et amélioration du preset `long`

**Problème identifié** : le preset `long` était trop conservateur.
- Recuit simulé (RS) : 1200 itérations avec refroidissement 0.995 → la température descendait sous le seuil d'exploration utile (~1.4°C) après seulement **887 itérations** ; les 313 dernières étaient inutiles (descente pure)
- Recherche tabou : seulement 20 itérations × 100 voisins = 2000 évaluations, insuffisant pour s'extraire des optima locaux

**Correction appliquée** dans `src/solver.py` :
```python
LONG_PRESET = ExperimentPreset(
    name="long",
    sa_iterations=2500,
    sa_temperature=150.0,
    sa_cooling_rate=0.997,
    sa_neighbor_attempts=100,
    tabu_iterations=40,
    tabu_tenure=20,
    tabu_max_neighbors=150,
    repetitions=3,
)
```
Effet : avec cooling=0.997 et 2500 itérations, le RS explore utilement pendant ~1555 itérations (vs 887 avant, +75%). La tabou passe à 40×150=6000 évaluations vs 2000 (×3).

`rapport.tex` mis à jour : tableau des paramètres synchronisé avec le nouveau preset.

## Résultats CVRP `long` améliorés (2026-04-30)

Logs : `tmp/experiments/improved_long_cvrp.log`

| Instance | k | Init moy | SA moy | Tabou moy | Temps SA | Temps tabou |
|---|---|---|---|---|---|---|
| data101.vrp  | 8 | 3649.06 | **1488.99** | 1776.59 | 0.51 | 1.19 |
| data102.vrp  | 8 | 3647.26 | **1572.25** | 1846.33 | 0.56 | 1.33 |
| data1101.vrp | 9 | 4635.30 | **1971.79** | 2301.35 | 0.76 | 1.77 |
| data1102.vrp | 9 | 4783.86 | **1988.77** | 2344.61 | 0.74 | 1.94 |
| data111.vrp  | 8 | 3498.39 | **1531.17** | 1806.32 | 0.54 | 1.44 |
| data112.vrp  | 8 | 3629.29 | **1484.82** | 1831.06 | 0.70 | 1.62 |
| data1201.vrp | 2 | 4441.38 | **1531.84** | 1870.48 | 0.54 | 1.29 |
| data1202.vrp | 2 | 4483.64 | **1594.21** | 1892.68 | 0.62 | 1.43 |
| data201.vrp  | 2 | 3432.02 | **1276.75** | 1614.32 | 0.45 | 1.11 |
| data202.vrp  | 2 | 3451.40 | **1313.29** | 1525.08 | 0.52 | 1.21 |

Comparé à l'ancien preset : SA améliore de ~15-24%, Tabou de ~21-36% sur tout le corpus CVRP.
Meilleure valeur observée data101 CVRP (run individuel) : **1438.10**.

## Résultats VRPTW `long` améliorés — data101 seul à ce stade (2026-04-30)

Logs : `tmp/experiments/improved_long_vrptw.log` (en cours à 10:59)

| Instance | k | Init moy | SA moy | Tabou moy | Temps SA | Temps tabou |
|---|---|---|---|---|---|---|
| data101.vrp | 21 | 2127.09 | **1744.18** | **1746.76** | 38.22 | 163.55 |

Observations :
- RS et Tabou sont maintenant **quasi-identiques** sur data101 VRPTW (1744 vs 1747)
- RS était 1756 avant, Tabou 1853 avant → Tabou améliorée de -5.7%
- Les 9 autres instances VRPTW sont encore en cours

## Résultats VRPTW `long` améliorés — complets (2026-04-30)

Logs : `tmp/experiments/improved_long_vrptw.log`

| Instance | k | Init moy | SA moy | Tabou moy | Temps SA | Temps tabou |
|---|---|---|---|---|---|---|
| data101.vrp  | 21 | 2127.09 | 1744.18 | 1746.76 | 38.22  | 163.55 |
| data102.vrp  | 18 | 1794.68 | 1624.00 | 1536.16 | 6.23   | 28.60  |
| data1101.vrp | 18 | 2184.86 | 1800.45 | 1790.35 | 9.42   | 58.78  |
| data1102.vrp | 16 | 2035.58 | 1692.94 | 1652.58 | 8.23   | 31.51  |
| data111.vrp  | 14 | 1601.37 | 1321.15 | 1310.27 | 4.13   | 13.85  |
| data112.vrp  | 12 | 1434.70 | 1167.36 | 1182.16 | 4.27   | 15.17  |
| data1201.vrp | 5  | 1970.77 | 1704.66 | 1506.00 | 4.13   | 16.49  |
| data1202.vrp | 4  | 1948.06 | 1604.65 | 1499.79 | 3.67   | 11.09  |
| data201.vrp  | 5  | 1640.28 | 1513.91 | 1310.55 | 3.71   | 11.54  |
| data202.vrp  | 5  | 1600.20 | 1514.41 | 1238.85 | 1.92   | 5.04   |

Nouveaux constats VRPTW :
- Tabou meilleure sur 8/10 instances (était 8/10 avant, mais les marges sont plus grandes)
- data101 : quasi-parité (SA=1744, Tabou=1747, écart < 3)
- data112 : SA légèrement meilleure (1167 vs 1182)
- data202 : Tabou domine nettement (1239 vs 1514)

## État final à 11:30 (2026-04-30)

- CVRP `long` : terminé → `tmp/experiments/improved_long_cvrp.log`
- VRPTW `long` : terminé → `tmp/experiments/improved_long_vrptw.log`
- `rapport.tex` : toutes les tables et analyses textuelles mises à jour
- `rapport.pdf` : recompilé avec succès (34 pages)
- `src/solver.py` : preset `long` mis à jour

## Diagnostic gap data101 VRPTW (2026-04-30)

Constat : SA data101 VRPTW converge autour de 1744 (meilleur run 1706), alors que ~1650 est obtenu par d'autres implémentations.

Diagnostic confirmé par tests :
- `find_minimum_vehicles` → 21 véhicules (greedy construction, borne LB=8)
- Taux d'échec voisinage = 3% seulement → pas un problème de faisabilité
- 5000 itérations → 1711 (quasi-identique à 2500 iter → 1707) : le gap n'est PAS un problème de budget
- Nombre de véhicules reste 21 en fin d'optimisation : aucune route jamais vidée avec nos opérateurs

**Cause réelle** : opérateurs de voisinage trop limités.
- Nos opérateurs : relocate (1 client), swap (2 clients), 2-opt intra-route
- Manquant : Or-opt(2) (déplacer 2 clients consécutifs), 2-opt* inter-routes

**Décision** : option 1 acceptée — documenter le gap dans le rapport plutôt que d'implémenter Or-opt(2) à J-4.

## Rapport mis à jour (2026-04-30 session 2)

- Section "Structure du code" : arborescence complète avec tous les fichiers (construction.py ajouté, data/ et figures/ ajoutés)
- Nouvelle section "Mode opératoire" : guide utilisateur complet (prérequis, commandes, options)
- Cas data101 VRPTW : mention du gap ~5% par rapport aux ~1650 théoriques
- Section "Limites" : bullet Or-opt(2)/2-opt* explicite
- Conclusion : mention spécifique des opérateurs manquants
- `generate_figures.py` exécuté → 5 figures régénérées avec nouvelles valeurs
- `rapport.pdf` recompilé (35 pages)

## Ce qui reste avant rendu

- Relire visuellement `rapport.pdf` une dernière fois
- Vérifier que la page de garde a les bons noms (El Bouazzaoui Ali / Nadir Ayoub ✓)
- Créer le ZIP pour Moodle
- Nettoyer les fichiers temporaires dans `tmp/` si voulu
