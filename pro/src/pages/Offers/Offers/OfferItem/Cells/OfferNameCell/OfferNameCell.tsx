import React from 'react'
import { Link } from 'react-router-dom'

import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_SOLD_OUT,
} from 'core/Offers/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import fullErrorIcon from 'icons/full-error.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'
import { pluralize } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

import styles from '../../OfferItem.module.scss'

import { getRemainingTime, getDate, shouldDisplayWarning } from './utils'

export interface OfferNameCellProps {
  offer: Offer
  editionOfferLink: string
  audience: Audience
}

const OfferNameCell = ({
  offer,
  editionOfferLink,
  audience,
}: OfferNameCellProps) => {
  const getDateInformations = () => {
    const {
      stocks,
      venue: { departementCode },
    } = offer
    const { beginningDatetime } = stocks[0] ?? {}
    /* istanbul ignore next: DEBT, TO FIX */
    if (offer.isShowcase || !beginningDatetime || !departementCode) {
      return null
    }

    /* istanbul ignore next: DEBT, TO FIX */
    const stockSize = offer.stocks ? offer.stocks.length : 0
    return stockSize === 1
      ? formatLocalTimeDateString(
          beginningDatetime,
          departementCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : pluralize(stockSize, 'date')
  }

  const computeNumberOfSoldOutStocks = () =>
    offer.stocks.filter((stock) => stock.remainingQuantity === 0).length

  const shouldShowIndividualWarning =
    audience === Audience.INDIVIDUAL &&
    computeNumberOfSoldOutStocks() > 0 &&
    offer.status !== OFFER_STATUS_SOLD_OUT

  const shouldShowCollectiveWarning =
    audience === Audience.COLLECTIVE &&
    offer.educationalBooking?.booking_status === OFFER_STATUS_PENDING &&
    shouldDisplayWarning(offer.stocks[0])

  return (
    <td className={styles['title-column']}>
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
      {offer.isEvent && (
        <span className={styles['stocks']}>
          {getDateInformations()}
          {shouldShowIndividualWarning && (
            <div>
              <SvgIcon
                className={styles['sold-out-icon']}
                src={fullErrorIcon}
                alt="Attention"
              />

              <span className={styles['sold-out-dates']}>
                <SvgIcon
                  className={styles['sold-out-icon']}
                  src={fullErrorIcon}
                  alt="Attention"
                />
                {pluralize(computeNumberOfSoldOutStocks(), 'date épuisée')}
              </span>
            </div>
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
      {offer.productIsbn && (
        <div className={styles['isbn']}>{offer.productIsbn}</div>
      )}
    </td>
  )
}

export default OfferNameCell
