import {
  AddressResponseIsLinkedToVenueModel,
  GetOfferVenueResponseModel,
} from 'apiClient/v1'
import { computeAddressDisplayName } from 'repository/venuesService'

import style from './VenueDetails.module.scss'

interface VenueDetailsProps {
  venue: GetOfferVenueResponseModel
  address?: AddressResponseIsLinkedToVenueModel | null
  withdrawalDetails?: string
}

export const VenueDetails = ({
  venue,
  address,
  withdrawalDetails,
}: VenueDetailsProps): JSX.Element => {
  const { street, postalCode, city } = address || venue

  const label = address ? address.label || '' : venue.publicName || venue.name

  const venueAddressString = computeAddressDisplayName(
    {
      street,
      postalCode: postalCode || '',
      city: city || '',
    },
    false
  )

  return (
    <div className={style['venue-details']}>
      <div className={style['section']}>
        <div className={style['title']}>Localisation</div>
        <div className={style['sub-title']}>Intitulé</div>
        <div className={style['text']}>{label || '- -'}</div>
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
