import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import { ReactComponent as PendingIcon } from 'components/pages/Offers/Offer/Confirmation/assets/pending.svg'
import { ReactComponent as ValidateIcon } from 'components/pages/Offers/Offer/Confirmation/assets/validate.svg'
import { DisplayOfferInAppLink } from 'components/pages/Offers/Offer/DisplayOfferInAppLink'
import { OFFER_STATUS_PENDING } from 'core/Offers/constants'

const Confirmation = ({ offer, setOffer, reloadOffer }) => {
  const [isLoading, setIsLoading] = useState(true)
  const resetOffer = useCallback(() => {
    setOffer(null)
  }, [setOffer])

  useEffect(() => {
    reloadOffer()
    setIsLoading(false)
  }, [])

  if (isLoading) return <Spinner />

  const isPendingOffer = offer.status === OFFER_STATUS_PENDING

  let queryString = `?structure=${offer.venue.managingOfferer.id}&lieu=${offer.venueId}`

  return (
    <div className="offer-confirmation">
      {isPendingOffer ? (
        <div>
          <PendingIcon className="oc-pending" />
          <h2 className="oc-title">Offre en cours de validation</h2>
          <p className="oc-details">
            Votre offre est en cours de validation par l’équipe pass Culture,
            nous vérifions actuellement son éligibilité.
            <b> Cette vérification pourra prendre jusqu’à 72h.</b> Vous recevrez
            un email de confirmation une fois votre offre validée et disponible
            à la réservation.
          </p>
        </div>
      ) : (
        <div>
          <ValidateIcon className="oc-validate" />
          <h2 className="oc-title">Offre créée !</h2>
          <p className="oc-details">
            Votre offre est désormais disponible à la réservation sur
            l’application pass Culture.
          </p>
        </div>
      )}
      <div className="oc-actions">
        <DisplayOfferInAppLink nonHumanizedId={offer.nonHumanizedId} />
        <Link
          className="primary-link"
          onClick={resetOffer}
          to={`/offre/creation/individuel${queryString}`}
        >
          Créer une nouvelle offre
        </Link>
      </div>
    </div>
  )
}

Confirmation.propTypes = {
  offer: PropTypes.shape().isRequired,
  setOffer: PropTypes.func.isRequired,
}

export default Confirmation
