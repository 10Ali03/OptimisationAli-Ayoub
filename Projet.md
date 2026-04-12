# Projet — Optimisation Discrète

**Filière :** Informatique  
**Enseignant :** Stéphane Bonnevay — Polytech Lyon 1

## Sujet

**Projet : Vehicle Routing Problem with Time Windows (VRPTW)**

Ce projet est à réaliser par groupe de **2 étudiants maximum**.

**Date limite :** lundi 4 mai à 07h00  
**Règle :** 5 points de moins par jour de retard.

## Objectif

L’objectif est de trouver des solutions au problème du **VRPTW** en utilisant **2 métaheuristiques** parmi les méthodes vues en cours.

Le **VRPTW** consiste à déterminer un ensemble d’itinéraires, commençant et se terminant au dépôt, qui couvrent un ensemble de clients.

Chaque client :
- a une demande spécifique,
- est visité une seule fois,
- est visité par un seul véhicule.

Tous les véhicules :
- ont la même capacité `C`,
- transportent un seul type de marchandises.

Aucun véhicule ne peut desservir plus de clients que sa capacité `C` ne le permet.

L’objectif est de **réduire au minimum la distance totale parcourue** par l’ensemble des véhicules.
Le **nombre de véhicules utilisés** est à déterminer, et **n’est pas limité**.

> Il est conseillé, mais pas obligatoire, de faire une visualisation des tournées afin de pouvoir vérifier la validité de vos opérateurs de voisinage et de vos résultats.

## Travail demandé

### 1. Modélisation

Modéliser ce problème et mettre en place la structure de votre code.

### 2. Nombre minimal de véhicules

Pour chaque jeu de données, déterminer le **nombre minimum de véhicules** à utiliser.

Faire le projet :
- d’abord **sans tenir compte des fenêtres de temps**,
- puis **en les prenant en compte**.

### 3. Générateur aléatoire

Créer un **générateur aléatoire de solutions**.

### 4. Métaheuristiques

Implémenter **2 métaheuristiques** et les tester sur les fichiers de données téléchargeables sur **Moodle**, avec :
- un protocole de tests clairement expliqué,
- une analyse des résultats.

Chaque fichier contient une liste de clients avec :
- leurs coordonnées euclidiennes,
- la quantité d’articles demandés.

Le client numéro `0` correspond au **dépôt**.

### 5. Comparaison des algorithmes

Comparer les deux algorithmes en termes de :
- temps d’exécution,
- qualité des solutions obtenues,
- nombre de solutions générées,
- influence des structures de voisinage utilisées,
- influence des valeurs des paramètres.

Discuter les résultats.

### 6. Bonus

En utilisant un package de programmation linéaire, essayer de déterminer à partir de quelle limite (par exemple le **nombre de clients**) il devient difficile d’obtenir une solution, en utilisant la modélisation donnée en cours.

Pour cela, construire vous-même des jeux de données de plus en plus gros à partir d’un des jeux de données fournis.

## Livrables

Vous devez fournir :
- un **rapport en PDF** expliquant et illustrant l’ensemble du travail réalisé,
- le **code associé**, en indiquant comment l’exécuter.

Le tout devra être déposé dans un **fichier ZIP à votre nom** dans la **Zone de dépôt** du module Moodle associé au cours.
