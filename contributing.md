# Charte des codeurs pass-culture

## Global

  - Syntaxe des imports:

      1. Imports par ordre alphabétique
      2. Une ligne de séparation entre librairies externes et modules internes
      3. Ne pas utiliser les imports/exports "default" de façon à forcer à ce que tout soit nommé pareil partout et faciliter la lisibilité. Dans la plupart des cas, donc, ça revient à faire "import { fooSelector } from Bar" plutot que "import fooSelector from Bar".

      ```
      import os
      from flask import current_app

      from models import Event, User
      from utils.human_ids import humanize
      ```

      ```
      import { requestData } from 'pass-culture-shared'
      import React from 'react'
      import { connect } from 'react-redux'
      import { withRouter } form 'react-router'
      import { compose } from 'redux'

      import OccasionItem from './OccasionItem'
      import Icon from '../layout/Icon'
      import { showModal } from '../components/reducers/modal'
      import { THUMBS_URL } form '../utils/config'
      ```

  - Nomination des variables, si possible:
    * arrays avec des pluriels, exemple : data, events
    * object avec des singuliers, si les objets sont des
      hmaps de variables de même type, alors on peut le specifier
      avec des noms de type objectsByName, eventsById, etc...

## Backend Python

  - Casse: underscore case pour les variables, mais camelCase pour les clés des objets postgres

## Frontend Javascript

  - Casse: camelCase pour les variables, sauf CamelCase pour les classes

  - Syntaxe des reducers:
    * action: \<VERBE\>\_\<REDUCER_NAME\>\_\<COMPLEMENT D OBJECT\> (UNDERSCORE_CASE):
      exemple: REQUEST_DATA_GET_MEDIATIONS, SHOW_MODAL
    * créateur d'action: \<verbe>\<reducerName\>\<complement d'object\> (camelCase)
      exemple: setUser, closeModal

  - Accesseurs:
    * utilisation préférentielle de lodash.get:
      exemple: get(ownProps, 'mediation.id') au lieu de ownProps.mediation && ownProps.mediation.id

  - Selecteurs:
    * Grouper les selecteurs par domaine fonctionnel
    * Un seul fichier par domaine fonctionel
    * On utilise des noms de la forme selectSomethingBySomecriterionAndSomeothercriterion
    * Pour les cachedSelector la fonction pour la clé de cache est nommée explicitement : mapArgsToCacheKey

  - Container / Composant
    * Action de renommage + split si possible
    * Page "Stock" coté Pro a refaire aux nouvelles normes

  - Container
    * Un container ne manipule pas le state
    * Pas d'accès direct au state
    * Il lit les informations via des selectors
    * On corrige de manière oportuniste

## Les étapes avant de passer un ticket en code review

- Respecter tous les points du `contributing.md` ;

- Nommer les messages de commit de la façon suivante `(PC-XXXX) : Ton message explicite` ;

- Faire un nombre résonnable de commit ;

- Faire un `rebase master` régulièrement ;

- Poser des tests unitaires sur tout nouveau code quand c'est pertinent ;

- Poser des tests end to end quand c'est un chemin critique (défini par le développeur) ;

- Vérifier que tous les tests sont verts en local **ET** sur CircleCI ;

- Recetter ce que l'on développe : UX/UI/Accessibilité/Sémantique ;

- Recetter sur différents navigateurs : Chrome, Firefox, Edge et Safari mobile ;

- Supprimer les erreurs JavaScript dans la console du navigateur et sur les tests unitaires ;

- Mettre le lien de la pull request dans le ticket Jira.
