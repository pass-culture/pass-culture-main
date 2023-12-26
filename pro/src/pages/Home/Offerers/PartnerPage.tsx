import React from 'react'
import { useLoaderData } from 'react-router-dom'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import { VenueEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Card } from '../Card'
import { HomepageLoaderData } from '../Homepage'

import styles from './PartnerPage.module.scss'

interface PartnerPageProps {
  offererId: string
  venue: GetOffererVenueResponseModel
}

export const PartnerPage = ({ offererId, venue }: PartnerPageProps) => {
  const { logEvent } = useAnalytics()
  const { venueTypes } = useLoaderData() as HomepageLoaderData
  const venueType = venueTypes.find(
    (venueType) => venueType.id === venue.venueTypeCode
  )

  return (
    <Card>
      <div className={styles['header']}>
        <div className={styles['image']}>
          Ajouter une image (TODO next ticket)
        </div>

        <div>
          <div className={styles['venue-type']}>{venueType?.label}</div>
          <div className={styles['venue-name']}>{venue.name}</div>
          <address className={styles['venue-address']}>{venue.address}</address>

          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: `/structures/${offererId}/lieux/${venue.id}?modification`,
              isExternal: false,
            }}
            onClick={() =>
              logEvent?.(VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK, {
                venue_id: venue.id,
              })
            }
          >
            Gérer ma page
          </ButtonLink>
        </div>
      </div>
    </Card>
  )
}
