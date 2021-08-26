/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'

import RouteLeavingGuard from 'components/layout/RouteLeavingGuard/RouteLeavingGuard'

import { ReactComponent as IllusError } from './assets/illus-erreur.svg'

const LeavingOfferCreationDialog = ({ shouldBlockNavigation, when }) => {
  return (
    <RouteLeavingGuard
      extraClassNames="exit-offer-creation-dialog"
      labelledBy="LEAVING_OFFER_CREATION_LABEL_ID"
      shouldBlockNavigation={shouldBlockNavigation}
      when={when}
    >
      <IllusError />
      <p>
        Voulez-vous quitter la création d’offre ?
      </p>
      <p>
        Votre offre ne sera pas sauvegardée et toutes les informations seront perdues
      </p>
    </RouteLeavingGuard>
  )
}

LeavingOfferCreationDialog.propTypes = {
  shouldBlockNavigation: PropTypes.func.isRequired,
  when: PropTypes.bool.isRequired,
}

export default LeavingOfferCreationDialog
