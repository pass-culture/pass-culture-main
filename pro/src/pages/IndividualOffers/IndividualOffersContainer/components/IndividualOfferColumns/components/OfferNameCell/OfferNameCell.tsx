import { Link } from 'react-router'

import { ListOffersOfferResponseModel } from '@/apiClient/v1'
import { OFFER_STATUS_SOLD_OUT } from '@/commons/core/Offers/constants'
import { FORMAT_DD_MM_YYYY_HH_mm } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { pluralize } from '@/commons/utils/pluralize'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { Tag } from '@/design-system/Tag/Tag'
import fullErrorIcon from '@/icons/full-error.svg'
import styles from '@/pages/IndividualOffers/IndividualOffersContainer/components/IndividualOfferColumns/components/Cells.module.scss'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import { Thumb } from '@/ui-kit/Thumb/Thumb'
import { Tooltip } from '@/ui-kit/Tooltip/Tooltip'

export interface OfferNameCellProps {
  offer: ListOffersOfferResponseModel
  offerLink: string
}

export const OfferNameCell = ({ offer, offerLink }: OfferNameCellProps) => {
  const getDateInformations = () => {
    const startDatetime = offer.stocks[0]
      ? offer.stocks[0].beginningDatetime
      : undefined

    let departmentCode = getDepartmentCode(offer)

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
    computeNumberOfSoldOutStocks() > 0 && offer.status !== OFFER_STATUS_SOLD_OUT

  return (
    <div className={styles['title-column']}>
      <Link className={styles['title-column-with-thumb']} to={offerLink}>
        <div className={styles['title-column-thumb']}>
          <Thumb url={offer.thumbUrl} />
        </div>
        <div>
          {offer.isShowcase && <Tag label="Offre vitrine" />}
          <div className={styles['title-column-name']}>{offer.name}</div>
          {offer.isEvent && (
            <span className={styles['stocks']}>
              {getDateInformations()}
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
          {offer.productIsbn && (
            <div className={styles['isbn']} data-testid="offer-isbn">
              {offer.productIsbn}
            </div>
          )}
        </div>
      </Link>
    </div>
  )
}
