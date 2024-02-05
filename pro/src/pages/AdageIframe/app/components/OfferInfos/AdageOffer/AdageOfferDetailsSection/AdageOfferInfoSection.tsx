import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { isCollectiveOfferTemplate } from 'core/OfferEducational'
import { getRangeToFrenchText, toDateStrippedOfTimezone } from 'utils/date'

import styles from '../AdageOffer.module.scss'

type AdageOfferInfoSectionProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

function getLocationForOfferVenue(
  offerVenue: CollectiveOfferResponseModel['offerVenue']
) {
  switch (offerVenue.addressType) {
    case OfferAddressType.OTHER: {
      return offerVenue.otherAddress
    }
    case OfferAddressType.SCHOOL: {
      return 'Le partenaire culturel se déplace dans les établissements scolaires.'
    }
    default: {
      return (
        <>
          <div>{offerVenue.publicName || offerVenue.name}</div>
          <div>
            {offerVenue.address}, {offerVenue.postalCode} {offerVenue.city}
          </div>
        </>
      )
    }
  }
}

export default function AdageOfferInfoSection({
  offer,
}: AdageOfferInfoSectionProps) {
  const offerVenue = offer.offerVenue

  const location = getLocationForOfferVenue(offerVenue)

  const dates =
    isCollectiveOfferTemplate(offer) &&
    ((offer.dates?.start &&
      offer.dates?.end &&
      getRangeToFrenchText(
        toDateStrippedOfTimezone(offer.dates.start),
        toDateStrippedOfTimezone(offer.dates.end)
      )) ||
      'Tout au long de l’année scolaire (l’offre est permanente)')

  return (
    <>
      <div className={styles['offer-section-group-item']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>
          Lieu où se déroulera l’offre
        </h3>
        {location}
      </div>

      <div className={styles['offer-section-group-item']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>Date</h3>
        {dates}
      </div>

      {offer.educationalPriceDetail && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Information sur le prix
          </h3>
          {offer.educationalPriceDetail}
        </div>
      )}
    </>
  )
}
