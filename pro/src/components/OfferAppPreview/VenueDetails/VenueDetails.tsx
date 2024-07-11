import React from 'react'

import { GetOfferVenueResponseModel } from 'apiClient/v1'

import style from './VenueDetails.module.scss'

interface VenueDetailsProps {
  venue: GetOfferVenueResponseModel
  withdrawalDetails?: string
}

export const VenueDetails = ({
  venue,
  withdrawalDetails,
}: VenueDetailsProps): JSX.Element => {
  const venueName = venue.publicName || venue.name
  const venueAddressString = [
    venueName,
    venue.street,
    venue.postalCode,
    venue.city,
  ]
    .filter((str) => Boolean(str))
    .join(' - ')

  return (
    <div className={style['venue-details']}>
      <div className={style['section']}>
        <div className={style['title']}>Où ?</div>
        <div className={style['sub-title']}>Adresse</div>
        <address className={style['text']}>{venueAddressString}</address>
        <div className={style['sub-title']}>Distance</div>
        <div className={style['text']}>- - km</div>
      </div>

      {withdrawalDetails && (
        <div className={style['section']}>
          <div className={style['title']}>Modalités de retrait</div>
          <div className={style['text']}>{withdrawalDetails}</div>
        </div>
      )}
    </div>
  )
}
