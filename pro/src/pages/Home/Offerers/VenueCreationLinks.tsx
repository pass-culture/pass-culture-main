import React from 'react'
import { useLocation } from 'react-router-dom'

import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

interface VenueCreationLinksProps {
  hasPhysicalVenue?: boolean
  hasVirtualOffers?: boolean
  offererId?: number
}

const VenueCreationLinks = ({
  hasPhysicalVenue,
  hasVirtualOffers,
  offererId,
}: VenueCreationLinksProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  const renderLinks = (insideCard: boolean) => {
    return (
      <div className="actions-container">
        <ButtonLink
          variant={insideCard ? ButtonVariant.PRIMARY : ButtonVariant.SECONDARY}
          link={{
            to: venueCreationUrl,
            isExternal: false,
          }}
          onClick={() => {
            logEvent?.(Events.CLICKED_CREATE_VENUE, {
              from: location.pathname,
              is_first_venue: !hasPhysicalVenue && !hasVirtualOffers,
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
          {renderLinks(true)}
        </div>
      </div>
    </div>
  )

  return (
    <div className="venue-banner">
      {!(hasPhysicalVenue || hasVirtualOffers)
        ? renderCard()
        : renderLinks(false)}
    </div>
  )
}

export default VenueCreationLinks
