import PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import { Redirect } from 'react-router'
import { Link } from 'react-router-dom'

import { ReactComponent as PendingIcon } from 'components/pages/Offers/Offer/Confirmation/assets/pending.svg'
import { ReactComponent as ValidateIcon } from 'components/pages/Offers/Offer/Confirmation/assets/validate.svg'
import OfferPreviewLink from 'components/pages/Offers/Offer/OfferPreviewLink/OfferPreviewLink'
import { OFFER_STATUS_PENDING } from 'components/pages/Offers/Offers/_constants'
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'

const Confirmation = ({ isCreatingOffer, location, offer, setOffer }) => {
  const resetOffer = useCallback(() => {
    setOffer(null)
  }, [setOffer])

  const isPendingOffer = offer.status === OFFER_STATUS_PENDING
  if (!isCreatingOffer && !isPendingOffer) {
    return <Redirect to={`/offres/${offer.id}/edition`} />
  }

  let queryString = ''
  const queryParams = queryParamsFromOfferer(location)
  if (queryParams.structure !== '') {
    queryString = `?structure=${queryParams.structure}`
  }

  if (queryParams.lieu !== '') {
    queryString += `&lieu=${queryParams.lieu}`
  }

  return (
    <div className="offer-confirmation">
      {isPendingOffer ? (
        <div>
          <PendingIcon className="oc-pending" />
          <h2 className="oc-title">
            Offre en cours de validation
          </h2>
          <p className="oc-details">
            Votre offre est en cours de validation par l’équipe du pass Culture. Vous recevrez un e-mail de confirmation une fois votre offre validée et disponible à la réservation.
          </p>
        </div>
      ) : (
        <div>
          <ValidateIcon className="oc-validate" />
          <h2 className="oc-title">
            Offre créée !
          </h2>
          <p className="oc-details">
            Votre offre est désormais disponible à la réservation sur l’application pass Culture.
          </p>
        </div>
      )}
      <div className="oc-actions">
        <OfferPreviewLink
          mediationId={offer.activeMediation ? offer.activeMediation.id : null}
          offerId={offer.id}
        />
        <Link
          className="primary-link"
          onClick={resetOffer}
          to={`/offres/creation${queryString}`}
        >
          Créer une nouvelle offre
        </Link>
      </div>
    </div>
  )
}

Confirmation.propTypes = {
  isCreatingOffer: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
  offer: PropTypes.shape().isRequired,
  setOffer: PropTypes.func.isRequired,
}

export default Confirmation
