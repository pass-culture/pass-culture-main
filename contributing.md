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
      import { showModal } from '../../reducers/modal'
      import { THUMBS_URL } form '../../utils/config'
      ```

  - Nomination des variables, si possible:
    * arrays avec des pluriels, exemple : data, events
    * object avec des singuliers, si les objets sont des
      hmaps de variables de même type, alors on peut le specifier
      avec des noms de type objectsByName, eventsById, etc...

## Backend Python

  - Casse: underscore case pour les variables, mais camelCase pour les clés des objets postgres

## Frontend Javascript

  - [AirBNB React Good Practices](https://github.com/airbnb/javascript/tree/master/react#naming)

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
    * on utilise des noms de la forme selectSomethingBySomecriterionAndSomeothercriterion
    * pour les cachedSelector la fonction pour la clé de cache est nommée explicitement : mapArgsToCacheKey
