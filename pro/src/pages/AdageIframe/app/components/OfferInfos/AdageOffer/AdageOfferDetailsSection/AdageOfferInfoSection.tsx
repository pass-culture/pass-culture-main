import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import { isCollectiveOfferBookable } from 'pages/AdageIframe/app/types'

import { getInterventionAreaLabelsToDisplay } from '../../../OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferInterventionArea'
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

export const AdageOfferInfoSection = ({
  offer,
}: AdageOfferInfoSectionProps) => {
  const offerVenue = offer.offerVenue

  const location = getLocationForOfferVenue(offerVenue)

  const interventionArea = offer.interventionArea

  const isOfferBookable = isCollectiveOfferBookable(offer)

  return (
    <>
      <div className={styles['offer-section-group-item-description']}>
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

      {!isOfferBookable &&
        offer.offerVenue.addressType !== OfferAddressType.OFFERER_VENUE &&
        interventionArea.length > 0 && (
          <div className={styles['offer-section-group-item']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              Zone de mobilité
            </h3>
            {getInterventionAreaLabelsToDisplay(interventionArea).map(
              (area, i) => (
                <span key={area}>
                  {i > 0 ? (
                    <span className={styles['offer-section-group-list-pipe']}>
                      {' '}
                      |{' '}
                    </span>
                  ) : (
                    ''
                  )}
                  {area}
                </span>
              )
            )}
          </div>
        )}

      {(isOfferBookable || offer.educationalPriceDetail) && (
        <div className={styles['offer-section-group-item-description']}>
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
