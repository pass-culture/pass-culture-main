import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import fullMoreIcon from 'icons/full-more.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import { VenueItem } from './VenueItem/VenueItem'
import styles from './Venues.module.scss'

interface VenuesProps {
  venues: GetOffererVenueResponseModel[]
  offererId: number
}

export const Venues = ({ venues, offererId }: VenuesProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  const { logEvent } = useAnalytics()

  return (
    <div className={styles['section']}>
      <div className={styles['main-list-title']}>
        <h2>Lieux</h2>
        <ButtonLink
          link={{
            to: venueCreationUrl,
            isExternal: false,
          }}
          onClick={() => {
            logEvent(Events.CLICKED_ADD_VENUE_IN_OFFERER, {
              from: location.pathname,
            })
          }}
          icon={fullMoreIcon}
          className={styles['main-list-title-button']}
        >
          Ajouter un lieu
        </ButtonLink>
      </div>

      <ul className={styles['venue-list']}>
        {venues.map((venue) => (
          <VenueItem key={venue.id} venue={venue} offererId={offererId} />
        ))}
      </ul>
    </div>
  )
}
