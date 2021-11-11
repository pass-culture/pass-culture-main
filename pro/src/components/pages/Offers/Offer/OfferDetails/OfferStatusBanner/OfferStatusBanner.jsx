/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'components/pages/Offers/Offers/_constants'
import { CGU_URL } from 'utils/config'

const OfferStatusBanner = ({ status }) => {
  return status === OFFER_STATUS_REJECTED ? (
    <Banner
      href={CGU_URL}
      linkTitle="Consulter les Conditions Générales d’Utilisation"
    >
      Votre offre a été refusée car elle ne respecte pas les Conditions Générales d’Utilisation du pass. Un e-mail contenant les conditions d’éligibilité d’une offre a été envoyé à l’adresse e-mail attachée à votre compte.
    </Banner>
  ) : (
    <Banner type="notification-info">
      Votre offre est en cours de validation par l’équipe du pass Culture. Une fois validée, vous recevrez un e-mail de confirmation et votre offre sera automatiquement mise en ligne.
    </Banner>
  )
}

OfferStatusBanner.propTypes = {
  status: PropTypes.oneOf([OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING]).isRequired,
}

export default OfferStatusBanner
