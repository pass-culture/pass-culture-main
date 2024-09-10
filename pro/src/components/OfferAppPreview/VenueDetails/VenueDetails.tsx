import {
  AddressResponseIsEditableModel,
  GetOfferVenueResponseModel,
} from 'apiClient/v1'

import style from './VenueDetails.module.scss'

interface VenueDetailsProps {
  venue: GetOfferVenueResponseModel
  address?: AddressResponseIsEditableModel | null
  withdrawalDetails?: string
}

export const VenueDetails = ({
  venue,
  address,
  withdrawalDetails,
}: VenueDetailsProps): JSX.Element => {
  const addressObj = address || venue

  const label = address ? address.label : venue.publicName || venue.name

  const venueAddressString = [
    label,
    addressObj.street,
    addressObj.postalCode,
    addressObj.city,
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
