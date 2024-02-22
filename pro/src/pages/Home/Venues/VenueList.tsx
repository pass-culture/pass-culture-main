import React from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'

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
  const virtualVenue = getVirtualVenueFromOfferer(offerer)
  const basePhysicalVenues = getPhysicalVenuesFromOfferer(offerer)

  const physicalVenues = basePhysicalVenues.filter(
    (venue) => !venue.isPermanent
  )

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
