import {
  CollectiveLocationType,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  GetCollectiveOfferLocationModel,
  OfferAddressType,
} from 'apiClient/adage'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
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

export function getLocationForOfferVenue(
  offerVenue: CollectiveOfferResponseModel['offerVenue']
) {
  switch (offerVenue.addressType) {
    case OfferAddressType.OTHER:
      return offerVenue.otherAddress
    case OfferAddressType.SCHOOL:
      return 'Le partenaire culturel se déplace dans les établissements scolaires.'
    case OfferAddressType.OFFERER_VENUE:
    default:
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

export function getLocation(
  location: GetCollectiveOfferLocationModel,
  header: boolean = false
): JSX.Element | string {
  if (location.locationType === CollectiveLocationType.TO_BE_DEFINED) {
    return 'À déterminer avec l’enseignant'
  }

  if (location.locationType === CollectiveLocationType.SCHOOL) {
    return header
      ? 'Dans l’établissement scolaire'
      : 'Le partenaire culturel se déplace dans les établissements scolaires.'
  }

  return (
    <div>
      {location.address?.label} - {location.address?.street},{' '}
      {location.address?.postalCode}, {location.address?.city}
    </div>
  )
}

export const AdageOfferInfoSection = ({
  offer,
}: AdageOfferInfoSectionProps) => {
  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const location =
    isCollectiveOaActive && offer.location
      ? getLocation(offer.location)
      : getLocationForOfferVenue(offer.offerVenue)

  const interventionArea = offer.interventionArea

  const isOfferBookable = isCollectiveOfferBookable(offer)

  return (
    <>
      <div className={styles['offer-section-group-item-description']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>
          Localisation de l’offre
        </h3>
        {location}
      </div>

      {offer.location &&
        offer.location.locationType === CollectiveLocationType.TO_BE_DEFINED &&
        offer.location.locationComment && (
          <div className={styles['offer-section-group-item']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              Commentaire
            </h3>
            {offer.location.locationComment}
          </div>
        )}

      <div className={styles['offer-section-group-item']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>
          {isOfferBookable &&
          offer.stock.startDatetime === offer.stock.endDatetime
            ? 'Date'
            : 'Dates'}
        </h3>
        {isOfferBookable
          ? getFormattedDatesForBookableOffer(offer)
          : getFormattedDatesForTemplateOffer(offer)}
      </div>

      {!isOfferBookable &&
        offer.offerVenue.addressType !== OfferAddressType.OFFERER_VENUE &&
        interventionArea.length > 0 && (
          <div className={styles['offer-section-group-item']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              {isCollectiveOaActive
                ? 'Départements de mobilité'
                : 'Zone de mobilité'}
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
          {isOfferBookable
            ? offer.stock.educationalPriceDetail
            : offer.educationalPriceDetail}
        </div>
      )}
    </>
  )
}
