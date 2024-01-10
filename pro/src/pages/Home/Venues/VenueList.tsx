import React from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import useActiveFeature from 'hooks/useActiveFeature'

import {
  getVirtualVenueFromOfferer,
  getPhysicalVenuesFromOfferer,
} from '../venueUtils'

import { Venue } from './Venue'
import styles from './Venue.module.scss'

export interface VenueListProps {
  offerer: GetOffererResponseModel
}

export const VenueList = ({ offerer }: VenueListProps) => {
  const isPartnerPageActive = useActiveFeature('WIP_PARTNER_PAGE')
  const virtualVenue = getVirtualVenueFromOfferer(offerer)
  const basePhysicalVenues = getPhysicalVenuesFromOfferer(offerer)

  const physicalVenues = isPartnerPageActive
    ? basePhysicalVenues.filter((venue) => !venue.isPermanent)
    : basePhysicalVenues

  const indexLastPhysicalVenues = physicalVenues.length - 1

  return (
    <div className={styles['venue-list']}>
      {virtualVenue && (
        <Venue venue={virtualVenue} offerer={offerer} isFirstVenue />
      )}

      {physicalVenues?.map((venue, index) => (
        <Venue
          key={offerer.id + '-' + venue.id}
          venue={venue}
          offerer={offerer}
          isFirstVenue={index === indexLastPhysicalVenues}
        />
      ))}
    </div>
  )
}
