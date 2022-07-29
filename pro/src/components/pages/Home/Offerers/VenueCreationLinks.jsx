import PropTypes from 'prop-types'
import React from 'react'
import { useSelector } from 'react-redux'
import { Link, useLocation } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import { isAPISireneAvailable } from 'store/features/selectors'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

const VenueCreationLinks = ({
  hasPhysicalVenue,
  hasVirtualOffers,
  offererId,
}) => {
  const isVenueCreationAvailable = useSelector(isAPISireneAvailable)
  const logEvent = useSelector(state => state.app.logEvent)
  const location = useLocation()

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  const renderLinks = ({ insideCard }) => {
    return (
      <div className="actions-container">
        <Link
          className={insideCard ? 'primary-link' : 'secondary-link'}
          onClick={() => {
            logEvent(Events.CLICKED_CREATE_VENUE, { from: location.pathname })
            logEvent(Events.CLICKED_ADD_FIRST_VENUE_IN_OFFERER, {
              from: location.pathname,
            })
          }}
          to={venueCreationUrl}
        >
          {!hasPhysicalVenue ? 'Créer un lieu' : 'Ajouter un lieu'}
        </Link>

        <Link
          className="secondary-link"
          onClick={() =>
            logEvent(Events.CLICKED_CREATE_OFFER, {
              from: location.pathname,
              offerer_id: offererId,
            })
          }
          to={`/offre/creation?structure=${offererId}`}
        >
          Créer une offre
        </Link>
      </div>
    )
  }

  const renderCard = () => (
    <div className="h-card" data-testid="offerers-creation-links-card">
      <div className="h-card-inner">
        <h3 className="h-card-title">Lieux</h3>

        <div className="h-card-content">
          <p>
            Avant de créer votre première offre physique vous devez avoir un
            lieu
          </p>
          {renderLinks({ insideCard: true })}
        </div>
      </div>
    </div>
  )

  return (
    <div className="venue-banner">
      {!(hasPhysicalVenue || hasVirtualOffers)
        ? renderCard()
        : renderLinks({ insideCard: false })}
    </div>
  )
}

VenueCreationLinks.propTypes = {
  hasPhysicalVenue: PropTypes.bool.isRequired,
  hasVirtualOffers: PropTypes.bool.isRequired,
  offererId: PropTypes.string.isRequired,
}

export default VenueCreationLinks
