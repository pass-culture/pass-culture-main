import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'

import { Venue } from './Venue'
import styles from './Venue.module.scss'

interface VenueListProps {
  physicalVenues: GetOffererVenueResponseModel[]
  selectedOffererId: number
  virtualVenue: GetOffererVenueResponseModel | null
  offererHasBankAccount: boolean
  hasNonFreeOffer: boolean
}

export const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
  offererHasBankAccount,
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
          isVirtual
          isFirstVenue
          offererId={selectedOffererId}
          offererHasCreatedOffer={offererHasCreatedOffer}
          offererHasBankAccount={offererHasBankAccount}
          hasNonFreeOffer={hasNonFreeOffer}
        />
      )}

      {physicalVenues?.map((venue, index) => (
        <Venue
          key={selectedOffererId + '-' + venue.id}
          venue={venue}
          isFirstVenue={index === indexLastPhysicalVenues}
          offererId={selectedOffererId}
          offererHasCreatedOffer={offererHasCreatedOffer}
          offererHasBankAccount={offererHasBankAccount}
          hasNonFreeOffer={hasNonFreeOffer}
        />
      ))}
    </div>
  )
}
