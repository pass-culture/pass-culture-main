import cn from 'classnames'
import React from 'react'

import style from './VenueDetails.module.scss'

export interface IVenueDetailsProps {
  name: string
  publicName?: string
  address: string
  postalCode: string
  city: string
  withdrawalDetails?: string
}

const VenueDetails = ({
  name,
  publicName,
  address,
  postalCode,
  city,
  withdrawalDetails,
}: IVenueDetailsProps): JSX.Element => {
  const venueName = publicName || name
  const venueAddressString = [venueName, address, postalCode, city]
    .filter(str => Boolean(str))
    .join(' - ')

  return (
    <div className={style['venue-details']}>
      <div className={style['section']}>
        <div className={style['title']}>Où ?</div>
        <div className={style['sub-title']}>Adresse</div>
        <address className={cn(style['text'], style['venue-address'])}>
          {venueAddressString}
        </address>
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

export default VenueDetails
