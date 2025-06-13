import classNames from 'classnames'
import { Link } from 'react-router'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'commons/core/OfferEducational/types'
import { OFFER_STATUS_SOLD_OUT } from 'commons/core/Offers/constants'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import { pluralize } from 'commons/utils/pluralize'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import { Tag } from 'design-system/Tag/Tag'
import fullErrorIcon from 'icons/full-error.svg'
import styles from 'styles/components/Cells.module.scss'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Thumb } from 'ui-kit/Thumb/Thumb'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import { CELLS_DEFINITIONS } from '../../utils/cellDefinitions'

export interface OfferNameCellProps {
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  offerLink: string
  rowId: string
  displayLabel?: boolean
  displayThumb?: boolean
  className?: string
}

export const OfferNameCell = ({
  offer,
  offerLink,
  rowId,
  displayLabel = false,
  displayThumb = false,
  className,
}: OfferNameCellProps) => {
  const getDateInformations = () => {
    const startDatetime = offer.stocks[0]
      ? isOfferEducational(offer)
        ? offer.stocks[0].startDatetime
        : offer.stocks[0].beginningDatetime
      : undefined

    let departmentCode = ''
    // If that offer is not educational, it means it's an individual offer …
    if (!isOfferEducational(offer)) {
      // … so we want here to use the offer's address 'departmentCode'
      departmentCode = getDepartmentCode(offer)
    } else {
      // … else, use venue's departementCode for educational offers
      departmentCode = offer.venue.departementCode ?? ''
    }

    /* istanbul ignore next: DEBT, TO FIX */
    if (offer.isShowcase || !startDatetime || !departmentCode) {
      return null
    }

    /* istanbul ignore next: DEBT, TO FIX */
    const stockSize = offer.stocks.length
    return stockSize === 1
      ? formatLocalTimeDateString(
          startDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : pluralize(stockSize, 'date')
  }

  const computeNumberOfSoldOutStocks = () =>
    offer.stocks.filter((stock) => stock.remainingQuantity === 0).length

  const shouldShowIndividualWarning =
    !isOfferEducational(offer) &&
    computeNumberOfSoldOutStocks() > 0 &&
    offer.status !== OFFER_STATUS_SOLD_OUT

  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['title-column'],
        className
      )}
      headers={`${rowId} ${CELLS_DEFINITIONS.NAME.id}`}
    >
      <Link
        className={classNames({
          [styles['title-column-with-thumb']]: displayThumb,
        })}
        to={offerLink}
      >
        {displayThumb && (
          <div className={styles['title-column-thumb']}>
            <Thumb
              url={isOfferEducational(offer) ? offer.imageUrl : offer.thumbUrl}
            />
          </div>
        )}
        <div>
          {offer.isShowcase && <Tag label="Offre vitrine" />}
          <div className={styles['title-column-name']}>
            {displayLabel && (
              <span
                className={styles['offers-table-cell-mobile-label']}
                aria-hidden={true}
              >
                {`${CELLS_DEFINITIONS.NAME.title} :`}
              </span>
            )}
            {offer.name}
          </div>
          {(isOfferEducational(offer) || offer.isEvent) && (
            <span className={styles['stocks']}>
              {!isOfferEducational(offer) &&
                offer.isEvent &&
                getDateInformations()}
              {shouldShowIndividualWarning && (
                <Tooltip
                  content={pluralize(
                    computeNumberOfSoldOutStocks(),
                    'date épuisée'
                  )}
                >
                  <button type="button" className={styles['sold-out-button']}>
                    <SvgIcon
                      className={styles['sold-out-icon']}
                      src={fullErrorIcon}
                      alt="Attention"
                      width="16"
                    />
                  </button>
                </Tooltip>
              )}
            </span>
          )}
          {!isOfferEducational(offer) && offer.productIsbn && (
            <div className={styles['isbn']} data-testid="offer-isbn">
              {offer.productIsbn}
            </div>
          )}
        </div>
      </Link>
    </td>
  )
}
