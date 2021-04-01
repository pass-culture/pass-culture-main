import PropTypes from 'prop-types'
import React from 'react'

import { ReactComponent as ValidateIcon } from 'components/pages/Offers/Offer/Confirmation/assets/validate.svg'
import OfferPreviewLink from 'components/pages/Offers/Offer/OfferPreviewLink/OfferPreviewLink'

const Confirmation = ({ offer }) => (
  <div className="offer-confirmation">
    <ValidateIcon className="oc-validate" />
    <div className="oc-title">
      {'Offre créée !'}
    </div>
    <p className="oc-details">
      {'Votre offre est désormais disponible à la réservation sur l’application pass Culture.'}
    </p>
    <div className="oc-actions">
      <OfferPreviewLink
        mediationId={offer.activeMediation ? offer.activeMediation.id : null}
        offerId={offer.id}
      />
      <a
        className="primary-link"
        href="/offres/creation"
      >
        {'Créer une nouvelle offre'}
      </a>
    </div>
  </div>
)

Confirmation.propTypes = {
  offer: PropTypes.shape().isRequired,
}

export default Confirmation
