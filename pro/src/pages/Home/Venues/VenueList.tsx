import React from 'react'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'

import { Venue } from './Venue'
import styles from './Venue.module.scss'

interface VenueListProps {
  offerer: GetOffererResponseModel
  physicalVenues: GetOffererVenueResponseModel[]
  virtualVenue: GetOffererVenueResponseModel | null
  hasNonFreeOffer: boolean
}

export const VenueList = ({
  offerer,
  physicalVenues,
  virtualVenue,
  hasNonFreeOffer,
}: VenueListProps) => {
  const offererHasCreatedOffer =
    virtualVenue?.hasCreatedOffer ||
    physicalVenues.some((venue) => venue.hasCreatedOffer)
  const indexLastPhysicalVenues = physicalVenues.length - 1

  return (
    <div className={styles['venue-list']}>
      {virtualVenue && (
        <Venue
          venue={virtualVenue}
          offerer={offerer}
          isVirtual
          isFirstVenue
          offererHasCreatedOffer={offererHasCreatedOffer}
          hasNonFreeOffer={hasNonFreeOffer}
        />
      )}

      {physicalVenues?.map((venue, index) => (
        <Venue
          key={offerer.id + '-' + venue.id}
          venue={venue}
          offerer={offerer}
          isFirstVenue={index === indexLastPhysicalVenues}
          offererHasCreatedOffer={offererHasCreatedOffer}
          hasNonFreeOffer={hasNonFreeOffer}
        />
      ))}
    </div>
  )
}
