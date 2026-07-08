import {
  CollectiveLocationType,
  type CollectiveOfferResponseModel,
  type CollectiveOfferTemplateResponseModel,
  type GetCollectiveOfferLocationModel,
} from '@/apiClient/adage'
import type { GetCollectiveOfferLocationModelV2 } from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { formatPrice } from '@/commons/utils/formatPrice'
import { isCollectiveOfferBookable } from '@/pages/AdageIframe/app/types'
import { ADDITIONAL_FEES } from '@/pages/CollectiveOffer/CollectiveOfferStock/components/AdditionalFeesForm/constants'

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
  location: GetCollectiveOfferLocationModel | GetCollectiveOfferLocationModelV2,
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

function formatAmount(amount: number): string {
  // we receive the price amounts in cents
  return formatPrice(amount / 100, { minimumFractionDigits: 0 })
}

export const AdageOfferInfoSection = ({
  offer,
}: AdageOfferInfoSectionProps) => {
  const interventionArea = offer.interventionArea

  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

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

      {offer.location?.locationType === CollectiveLocationType.TO_BE_DEFINED &&
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
          {isOfferBookable && isNewCollectivePriceEnabled ? (
            <div className={styles['price-details']}>
              <p>Prix total TTC : {formatAmount(offer.stock.price)}</p>
              {offer.stock.collectiveAdditionalFees?.length > 0 && (
                <>
                  {offer.stock.servicePrice != null && (
                    <p>
                      Dont le tarif de la prestation :{' '}
                      {formatAmount(offer.stock.servicePrice)}
                    </p>
                  )}
                  <p>Dont les frais annexes :</p>
                  <ul className={styles['additional-fees-list']}>
                    {offer.stock.collectiveAdditionalFees.map((fee) => (
                      <li key={`${fee.type}-${fee.amount}`}>
                        {fee.label ?? ADDITIONAL_FEES[fee.type]} :{' '}
                        {formatAmount(fee.amount)}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          ) : (
            isOfferBookable && <p>{getBookableOfferStockPrice(offer)}</p>
          )}
          {!isNewCollectivePriceEnabled &&
            (isOfferBookable
              ? offer.stock.educationalPriceDetail
              : offer.educationalPriceDetail)}
        </div>
      )}

      {isOfferBookable &&
        isNewCollectivePriceEnabled &&
        offer.additionalDetails && (
          <div className={styles['offer-section-group-item-description']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              Informations pratiques
            </h3>
            <p>{offer.additionalDetails}</p>
          </div>
        )}
    </>
  )
}
