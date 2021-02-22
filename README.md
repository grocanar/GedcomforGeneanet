# Greffons GedcomforGeneanet

Greffon pour améliorer l'export gedcom pour le rendre plus compatible avec Geneanet.

## Principe
Ce greffon est une "amélioration" de l'export gedcom de Geneanet. Il apporte les fonctionnalités suivantes:

* Export des témoins pour les événements
* Gestion des relations non maritales
* Inclusion des chemins des médias
* Exclure le nom des dépots dans les sources
* Suppression des chemins absolus dans le chemin des fichiers
* Suppression de l'attribut "ID Gramps fusionné"
* Ajout de la qualité des sources dans la description des sources
* Création d'une archive zip des médias concernés
* Suppression du support de la norme anychar du Gedcom 5.5
* Gestion des noms usuels
* Export des attributs des citations
* Export des informations de recensement d'un individu
* Export des lieux au format geneanet
* Indication du nom du lieu à la date de l'événement
* Indication des noms alternatifs des lieux
* Suppression de la structure adresse optionnelle


## Installation

Pour utiliser ce greffons il faut télécharger le fichier zip de la version souhaitée (avec XX = 42, 50, …) et

* Sous unix dezipper le fichier dans le répertoire $HOME/.gramps/grampsXX/plugins/
* Sous Windows dezipper le fichier dans le répertoire %APPDATA%\gramps\grampsXX\plugins (APPDATA vaut par défaut C:\USER%USERNAME%\AppData\Roaming avec %USERNAME% le nom de l'utilisateur sous Windows 10). Il faut néanmoins quitter GRAMPS avant de lancer l'opération.

## Fonctionnalités

### Export des témoins pour les événements

#### Cas particulier pour les baptèmes

Pour les baptèmes Si vous avez défini un role CUSTOM la personne de sexe masculin sera le Parrain et la personne de sexe féminin sera ma Marainne.

#### Témoins et rôle.

Pour les évenements individuels hors baptème tous les rôles sont assimilés à des témoins au vu de la pauvreté de la norme GEDCOM. 
Néanmoins l'option extend_role permet d'afficher le role mais celui sera alors sur deux lignes.

### Gestion des relations non maritales
Pour les couples non mariés leur statut n'est plus mariés. 

### Exclure le nom des dépots dans les sources

Cela permet d'exclure le nom du dépot dans le nom des sources.

### Suppression des chemins absolus dans le chemin des fichiers

Si l'option est activée cela supprime le chemin dans le tag FILE. 
Cela permet de supprimer en général une information utilisateur dans le fichier gedcom.

### Suppression de l'attribut "ID Gramps fusionné"

Cet attribut n'ayant pas d'intérêt celui est supprimé durant l'export.

### Suppression du support de la norme anychar du Gedcom 5.5

Geneanet n'implemente pas la norme anychar de la norme Gedcom5.3 qui impose de doubler les caractères @. Ainsi les dates exportés dans GRAMPS dans un calendrier alternatif ne sont pas bien rendues. Cette option permet de supprimer le doublement des @.


### Gestion des noms usuels

Permet d'exporter le prénom usuel en l'indiquant entre ".

### Export des attributs des citations

Permet d'exporter les attributs d'une citation. Cela permet par exemple d'indiquer l'url d'un acte.

### Export des informations de recensement d'un individu

Permet d'exporter pour un individu les informations dans un recensement sous formes de notes d'évenement.
###  Export des lieux au format geneanet
Geneanet impose un format pour les noms des lieux non compatible avec gramps. Cet option permet de generer le titre au format geneanet lors de l'export tout en conservant la génération automatique du titre dans GRAMPS.

### Indication du nom du lieu à la date de l'événement

Indique en note le nom du lieu à la date de l'événement.

### Indication des noms alternatifs des lieux

Indique en note les noms alternatifs du lieu.

### Suppression de la structure adresse optionnelle

La norme Gedcom permet l'inclusion d'une structure adresse optioennelle pour les lieux. C'est le focntionnement par défaut de GRAMPS. Mais cela entraine un souci lors de l'importation geneanet. 
