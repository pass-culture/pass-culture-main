import classNames from 'classnames'
import { Link } from 'react-router-dom'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'commons/core/OfferEducational/types'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_SOLD_OUT,
} from 'commons/core/Offers/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import { pluralize } from 'commons/utils/pluralize'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import fullErrorIcon from 'icons/full-error.svg'
import styles from 'styles/components/Cells.module.scss'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'


import { getDate, getRemainingTime, shouldDisplayWarning } from './utils'

export interface OfferNameCellProps {
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  editionOfferLink: string
  headers?: string
}

export const OfferNameCell = ({
  offer,
  editionOfferLink,
  headers,
}: OfferNameCellProps) => {
  const { isTooltipHidden, ...tooltipProps } = useTooltipProps({})
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
  )

  const useOffererAddressAsDataSourceEnabled = useActiveFeature(
    'WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE'
  )

  const getDateInformations = () => {
    const { stocks } = offer

    let departmentCode = ''
    // If that offer is not educational, it means it's an individual offer …
    if (!isOfferEducational(offer)) {
      // … so we want here to use the offer's address 'departmentCode' (under FF)
      departmentCode = getDepartmentCode({
        offer,
        useOffererAddressAsDataSourceEnabled,
      })
    } else {
      // … else, use venue's departementCode for educational offers
      departmentCode = offer.venue.departementCode ?? ''
    }

    const { beginningDatetime } = stocks[0] ?? {}
    /* istanbul ignore next: DEBT, TO FIX */
    if (offer.isShowcase || !beginningDatetime || !departmentCode) {
      return null
    }

    /* istanbul ignore next: DEBT, TO FIX */
    const stockSize = offer.stocks.length
    return stockSize === 1
      ? formatLocalTimeDateString(
          beginningDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : pluralize(stockSize, 'date')
  }

  const computeNumberOfSoldOutStocks = () =>
    offer.stocks.filter((stock) => stock.remainingQuantity === 0).length

  const shouldShowIndividualWarning =
    !offer.isEducational &&
    computeNumberOfSoldOutStocks() > 0 &&
    offer.status !== OFFER_STATUS_SOLD_OUT

  const shouldShowCollectiveWarning =
    isOfferEducational(offer) &&
    offer.booking?.booking_status === OFFER_STATUS_PENDING &&
    shouldDisplayWarning(offer.stocks[0]) &&
    !isCollectiveOffersExpirationEnabled

  return (
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['title-column']
      )}
      headers={headers}
    >
      {offer.isShowcase && (
        <Tag
          variant={TagVariant.SMALL_OUTLINE}
          className={styles['offer-template-tag']}
        >
          Offre vitrine
        </Tag>
      )}
      <Link
        className={styles['name']}
        title={`${offer.name} - éditer l’offre`}
        to={editionOfferLink}
      >
        {offer.name}
      </Link>

      {(isOfferEducational(offer) || offer.isEvent) && (
        <span className={styles['stocks']}>
          {!isOfferEducational(offer) && offer.isEvent && getDateInformations()}
          {isOfferEducational(offer) &&
            !isCollectiveOffersExpirationEnabled &&
            getDateInformations()}

          {shouldShowIndividualWarning && (
            <>
              <button
                type="button"
                {...tooltipProps}
                className={styles['sold-out-button']}
              >
                <SvgIcon
                  className={styles['sold-out-icon']}
                  src={fullErrorIcon}
                  alt="Attention"
                  width="16"
                />
              </button>
              {!isTooltipHidden && (
                <span className={styles['sold-out-dates']}>
                  <SvgIcon
                    className={styles['sold-out-icon']}
                    src={fullErrorIcon}
                    alt="Attention"
                    width="16"
                  />
                  {pluralize(computeNumberOfSoldOutStocks(), 'date épuisée')}
                </span>
              )}
            </>
          )}
          {shouldShowCollectiveWarning && (
            <div>
              &nbsp;
              <SvgIcon
                className={styles['sold-out-icon']}
                src={fullErrorIcon}
                alt="Attention"
              />
              <span className={styles['sold-out-dates']}>
                La date limite de réservation par le chef d’établissement est
                dans{' '}
                {`${
                  getRemainingTime(offer.stocks[0]) >= 1
                    ? pluralize(getRemainingTime(offer.stocks[0]), 'jour')
                    : 'moins d’un jour'
                } (${getDate(offer.stocks[0])})`}
              </span>
            </div>
          )}
        </span>
      )}

      {!isOfferEducational(offer) && offer.productIsbn && (
        <div className={styles['isbn']} data-testid="offer-isbn">
          {offer.productIsbn}
        </div>
      )}
    </td>
  )
}
