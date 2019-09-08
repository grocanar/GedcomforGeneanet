# Greffons GedcomforGeneanet

Greffon pour améliorer l'export gedcom pour le rendre plus compatible avec Geneanet.

## Principe
Ce greffon est une "amélioration" de l'export gedcom de Geneanet. Il apporte les fonctionnalités suivantes:

* Export des témoins pour les événements
* Gestion des relations non maritales
* Inclusion des chemins des médias
* Exclure le nom des dépots dans les sources
* Offuscation des sources généanet
* Suppression des chemins absolus dans le chemin des fichiers
* Suppression de l'attribut "ID Gramps fusionné"
* Ajout de la qualité des sources dans la description des sources
* Création d'une archive zip des médias concernés
* Embelissement des noms alternatifs
* Suppression du support de la norme anychar du Gedcom 5.5
* Gestion des noms usuels

## Installation

Pour utiliser ce greffons il faut télécharger le fichier zip de la version souhaité et 

* Sous unix dezipper le fichier dans le répertoire $HOME/.gramps/gramps42/plugins/
* Sous Windows deippter le fichiers dans le répertoire C:\Users\<~username>\AppData\Roaming\gramps\gramps42\plugins

## Fonctionnalités

### Export des témoins pour les événements

#### Cas particulier pour les baptèmes

Pour les baptèmes Si vous avez défini un role CUSTOM la personne de sexe masculin sera le Parrain et la personne de sexe féminin sera ma Marainne.

#### Témoins et rôle.

Pour les évenements individuels hors baptème tous les rôles sont assimilés à des témoins au vu de la pauvreté de la norme GEDCOM. 

### Gestion des relations non maritales
Pour les couples non mariés leur statut n'est plus mariés. 

### Exclure le nom des dépots dans les sources

Cela permet d'exclure le nom du dépot dans le nom des sources.

### Offuscation des sources généanet

Cet option permet d'augmenter le nombre d'étoiles dans le défunt système de Généanet.

### Suppression des chemins absolus dans le chemin des fichiers

Si l'option est activée cela supprime le chemin dans le tag FILE. 
Cela permet de supprimer en général une information utilisateur dans le fichier gedcom.

### Suppression de l'attribut "ID Gramps fusionné"

Cet attribut n'ayant pas d'intérêt celui est supprimé durant l'export

### Embelissement des noms alternatifs

Geneanet pour les noms alternatifs ne respectent pas la norme Gedcom qui impose de mettre les noms entre //. De ce fait on retrouve ces caractères dans le champs alias. Cette option permet de supprimer les // des noms alternatifs.

### Suppression du support de la norme anychar du Gedcom 5.5

Geneanet n'implemente pas la norme anychar de la norme Gedcom5.3 qui impose de doubler les caractères @. Ainsi les dates exportés dans GRAMPS dans un calendrier alternatif ne sont pas bien rendues. Cette option permet de supprimer le doublement des @.


### Gestion des noms usuels

Permet d'exporter le prénom usuel en l'indiquant entre "
