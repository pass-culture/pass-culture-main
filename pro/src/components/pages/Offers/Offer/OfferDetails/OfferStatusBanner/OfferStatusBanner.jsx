import PropTypes from 'prop-types'
import React from 'react'

import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import { Banner } from 'ui-kit'
import { CGU_URL } from 'utils/config'

const OfferStatusBanner = ({ status }) => {
  return status === OFFER_STATUS_REJECTED ? (
    <Banner
      href={CGU_URL}
      linkTitle="Consulter les Conditions Générales d’Utilisation"
    >
      Votre offre a été refusée car elle ne respecte pas les Conditions
      Générales d’Utilisation du pass. Un e-mail contenant les conditions
      d’éligibilité d’une offre a été envoyé à l’adresse e-mail attachée à votre
      compte.
    </Banner>
  ) : (
    <Banner type="notification-info">
      Votre offre est en cours de validation par l’équipe du pass Culture. Une
      fois validée, vous recevrez un e-mail de confirmation et votre offre sera
      automatiquement mise en ligne.
    </Banner>
  )
}

OfferStatusBanner.propTypes = {
  status: PropTypes.oneOf([OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING])
    .isRequired,
}

export default OfferStatusBanner
