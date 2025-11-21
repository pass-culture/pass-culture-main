import {
  CollectiveLocationType,
  type CollectiveOfferResponseModel,
  type CollectiveOfferTemplateResponseModel,
  type GetCollectiveOfferLocationModel,
} from '@/apiClient/adage'
import { isCollectiveOfferBookable } from '@/pages/AdageIframe/app/types'

import { getInterventionAreaLabelsToDisplay } from '../../../OffersInstantSearch/OffersSearch/Offers/utils/getInterventionAreaLabels'
import styles from '../AdageOffer.module.scss'
import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from '../utils/adageOfferDates'
import { getBookableOfferStockPrice } from '../utils/adageOfferStocks'

export type AdageOfferInfoSectionProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
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

  const addressLabel = location.location?.label
  return (
    <div>
      {addressLabel ? `${addressLabel} - ` : ''}
      {location.location?.street}, {location.location?.postalCode},{' '}
      {location.location?.city}
    </div>
  )
}

export const AdageOfferInfoSection = ({
  offer,
}: AdageOfferInfoSectionProps) => {
  const interventionArea = offer.interventionArea

  const isOfferBookable = isCollectiveOfferBookable(offer)

  return (
    <>
      {offer.location ? (
        <div className={styles['offer-section-group-item-description']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Localisation de l’offre
          </h3>
          {getLocation(offer.location)}
        </div>
      ) : null}

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
        offer.location?.locationType !== CollectiveLocationType.ADDRESS &&
        interventionArea.length > 0 && (
          <div className={styles['offer-section-group-item']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              Départements de mobilité
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
