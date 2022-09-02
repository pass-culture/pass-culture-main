import PropTypes from 'prop-types'
import React from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { isAPISireneAvailable } from 'store/features/selectors'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

const VenueCreationLinks = ({
  hasPhysicalVenue,
  hasVirtualOffers,
  offererId,
}) => {
  const isVenueCreationAvailable = useSelector(isAPISireneAvailable)
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  const renderLinks = ({ insideCard }) => {
    return (
      <div className="actions-container">
        <ButtonLink
          variant={insideCard ? ButtonVariant.PRIMARY : ButtonVariant.SECONDARY}
          link={{
            to: venueCreationUrl,
            isExternal: false,
          }}
          onClick={() => {
            logEvent?.(Events.CLICKED_CREATE_VENUE, { from: location.pathname })
            logEvent?.(Events.CLICKED_ADD_FIRST_VENUE_IN_OFFERER, {
              from: location.pathname,
            })
          }}
        >
          {!hasPhysicalVenue ? 'Créer un lieu' : 'Ajouter un lieu'}
        </ButtonLink>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{
            to: `/offre/creation?structure=${offererId}`,
            isExternal: false,
          }}
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_FORM_NAVIGATION_IN.HOME,
              to: OFFER_FORM_HOMEPAGE,
              used: OFFER_FORM_NAVIGATION_MEDIUM.HOME_BUTTON,
              isEdition: false,
            })
          }
        >
          Créer une offre
        </ButtonLink>
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
