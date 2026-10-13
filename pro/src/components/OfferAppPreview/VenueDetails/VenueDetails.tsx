import type { LocationResponseModel } from '@/apiClient/v1'
import { computeAddressDisplayName } from '@/commons/format/venuesService'

import style from './VenueDetails.module.scss'

interface VenueDetailsProps {
  address?: LocationResponseModel | null
  withdrawalDetails?: string
}

export const VenueDetails = ({
  address,
  withdrawalDetails,
}: VenueDetailsProps): JSX.Element => {
  function computeAddress() {
    let venueAddressString = '-'
    let label = '-'

    if (address) {
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
        <p className={style['title']}>Localisation</p>
        <p className={style['sub-title']}>Intitulé</p>
        <p className={style['text']}>{label || '- -'}</p>
        <p className={style['sub-title']}>Adresse</p>
        <address className={style['text']}>{venueAddressString}</address>
        <p className={style['sub-title']}>Distance</p>
        <p className={style['text']}>- - km</p>
      </div>

      {withdrawalDetails && (
        <div className={style['section']}>
          <p className={style['title']}>Modalités de retrait</p>
          <p className={style['text']}>{withdrawalDetails}</p>
        </div>
      )}
    </div>
  )
}
