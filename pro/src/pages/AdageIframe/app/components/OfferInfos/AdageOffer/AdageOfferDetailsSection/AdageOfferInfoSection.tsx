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
  const labelPrefix = addressLabel ? `${addressLabel} - ` : ''
  return `${labelPrefix}${location.location?.street}, ${location.location?.postalCode}, ${location.location?.city}`
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
          <p className={styles['offer-section-group-item-description-text']}>
            {getLocation(offer.location)}
          </p>
        </div>
      ) : null}

      {offer.location?.locationType === CollectiveLocationType.TO_BE_DEFINED &&
        offer.location.locationComment && (
          <div className={styles['offer-section-group-item']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              Commentaire
            </h3>
            <p className={styles['offer-section-group-item-text']}>
              {offer.location.locationComment}
            </p>
          </div>
        )}

      {isOfferBookable ? (
        <>
          <div className={styles['offer-section-group-item']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              {offer.stock.startDatetime === offer.stock.endDatetime
                ? 'Date'
                : 'Dates'}
            </h3>
            <p className={styles['offer-section-group-item-text']}>
              {getFormattedDatesForBookableOffer(offer)}
            </p>
          </div>
          <div className={styles['offer-section-group-item-description']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              Prix
            </h3>
            {isNewCollectivePriceEnabled ? (
              <div className={styles['price-details']}>
                <p
                  className={
                    styles['offer-section-group-item-description-text']
                  }
                >
                  Prix total TTC : {formatAmount(offer.stock.price)}
                </p>
                {offer.stock.collectiveAdditionalFees?.length > 0 && (
                  <>
                    {offer.stock.servicePrice != null && (
                      <p
                        className={
                          styles['offer-section-group-item-description-text']
                        }
                      >
                        Dont le tarif de la prestation :{' '}
                        {formatAmount(offer.stock.servicePrice)}
                      </p>
                    )}
                    <p
                      className={
                        styles['offer-section-group-item-description-text']
                      }
                    >
                      Dont les frais annexes :
                    </p>
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
              <>
                <p
                  className={
                    styles['offer-section-group-item-description-text']
                  }
                >
                  {getBookableOfferStockPrice(offer)}
                </p>
                <p
                  className={
                    styles['offer-section-group-item-description-text']
                  }
                >
                  {offer.stock.educationalPriceDetail}
                </p>
              </>
            )}
          </div>
          {isNewCollectivePriceEnabled && offer.additionalDetails && (
            <div className={styles['offer-section-group-item-description']}>
              <h3 className={styles['offer-section-group-item-subtitle']}>
                Informations pratiques
              </h3>
              <p
                className={styles['offer-section-group-item-description-text']}
              >
                {offer.additionalDetails}
              </p>
            </div>
          )}
        </>
      ) : (
        <>
          <div className={styles['offer-section-group-item']}>
            <h3 className={styles['offer-section-group-item-subtitle']}>
              Dates
            </h3>
            <p className={styles['offer-section-group-item-text']}>
              {getFormattedDatesForTemplateOffer(offer)}
            </p>
          </div>
          {offer.location?.locationType !== CollectiveLocationType.ADDRESS &&
            interventionArea.length > 0 && (
              <div className={styles['offer-section-group-item']}>
                <h3 className={styles['offer-section-group-item-subtitle']}>
                  Départements de mobilité
                </h3>
                <p className={styles['offer-section-group-item-text']}>
                  {getInterventionAreaLabelsToDisplay(interventionArea).join(
                    ' | '
                  )}
                </p>
              </div>
            )}
          {offer.educationalPriceDetail && (
            <div className={styles['offer-section-group-item-description']}>
              <h3 className={styles['offer-section-group-item-subtitle']}>
                Information sur le prix
              </h3>

              <p
                className={styles['offer-section-group-item-description-text']}
              >
                {offer.educationalPriceDetail}
              </p>
            </div>
          )}
        </>
      )}
    </>
  )
}
