import {
  AddressResponseIsLinkedToVenueModel,
  GetOfferVenueResponseModel,
} from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
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
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  function computeAddress() {
    let venueAddressString = '-'
    let label = '-'

    if (!isOfferAddressEnabled) {
      label = venue.publicName || venue.name
      venueAddressString = [label, venue.street, venue.postalCode, venue.city]
        .filter((str) => Boolean(str))
        .join(' - ')
    } else if (address) {
      const { street, postalCode, city } = address

      label = address.label || '-'

      venueAddressString = computeAddressDisplayName(
        {
          street,
          postalCode: postalCode || '',
          city: city || '',
        },
        false
      )
    }
    return { label, venueAddressString }
  }

  const { label, venueAddressString } = computeAddress()

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
