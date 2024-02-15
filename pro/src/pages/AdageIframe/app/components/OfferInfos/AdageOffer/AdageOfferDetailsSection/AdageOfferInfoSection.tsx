import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { isCollectiveOfferBookable } from 'core/OfferEducational'

import styles from '../AdageOffer.module.scss'
import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from '../utils/adageOfferDates'
import { getBookableOfferStockPrice } from '../utils/adageOfferStocks'

export type AdageOfferInfoSectionProps = {
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

  const isOfferBookable = isCollectiveOfferBookable(offer)

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
        {isOfferBookable
          ? getFormattedDatesForBookableOffer(offer)
          : getFormattedDatesForTemplateOffer(offer)}
      </div>

      {(isOfferBookable || offer.educationalPriceDetail) && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            {isOfferBookable ? 'Prix' : 'Information sur le prix'}
          </h3>
          {isOfferBookable && <p>{getBookableOfferStockPrice(offer)}</p>}
          {offer.educationalPriceDetail}
        </div>
      )}
    </>
  )
}
