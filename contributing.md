# Charte des codeurs pass-culture

## Global

  - Syntaxe des imports:

      1. Imports par ordre alphabétique
      2. Une ligne de séparation entre librairies externes et modules internes


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

## Backend Python

  - Casse: underscore case pour les variables, mais camelCase pour les clés des objets postgres

## Frontend Javascript

  - Casse: camelCase pour les variables, sauf CamelCase pour les classes

  - Syntaxe des reducers:
    * action: <VERBE>_<REDUCER_NAME>_<COMPLEMENT D OBJECT> (UNSERSCORE_CASE):
      exemple: REQUEST_DATA_GET_MEDIATIONS, SHOW_MODAL
    * créateur d'action: <verbe><reducerName><complement d'object> (camelCase)
      exemple: setUser, closeModal

  - Accesseurs:
    * utilisation préférentielle de lodash.get:
      exemple: get(ownProps, 'mediation.id') au lieu de ownProps.mediation && ownProps.mediation.id
