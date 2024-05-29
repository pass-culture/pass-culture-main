import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import {
  getVirtualVenueFromOfferer,
  getPhysicalVenuesFromOfferer,
} from '../venueUtils'

import styles from './VenueCreationLinks.module.scss'

interface VenueCreationLinksProps {
  offerer?: GetOffererResponseModel | null
}

export const VenueCreationLinks = ({ offerer }: VenueCreationLinksProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const virtualVenue = getVirtualVenueFromOfferer(offerer)
  const physicalVenues = getPhysicalVenuesFromOfferer(offerer)
  const hasVirtualOffers = Boolean(virtualVenue)
  const hasPhysicalVenue = physicalVenues.length > 0

  if (!hasPhysicalVenue) {
    return
  }

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offerer?.id}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <div className={styles['container']}>
      <div className={styles['add-venue-button']}>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{
            to: venueCreationUrl,
            isExternal: false,
          }}
          onClick={() => {
            logEvent(Events.CLICKED_CREATE_VENUE, {
              from: location.pathname,
              is_first_venue: !hasVirtualOffers,
            })
          }}
        >
          Ajouter un lieu
        </ButtonLink>
      </div>
    </div>
  )
}
