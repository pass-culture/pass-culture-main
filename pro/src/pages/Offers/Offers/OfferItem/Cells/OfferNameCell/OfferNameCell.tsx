import React from 'react'
import { Link } from 'react-router-dom'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import {
  OFFER_STATUS_DRAFT,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_SOLD_OUT,
} from 'core/Offers'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import useAnalytics from 'hooks/useAnalytics'
import { AlertFilledIcon } from 'icons'
import { Tag } from 'ui-kit'
import Icon from 'ui-kit/Icon/Icon'
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
  const { logEvent } = useAnalytics()

  const onOfferNameClick = () => {
    const isDraft = offer.status === OFFER_STATUS_DRAFT
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_FORM_NAVIGATION_IN.OFFERS,
      to: !isDraft
        ? OFFER_WIZARD_STEP_IDS.SUMMARY
        : OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_TITLE,
      isEdition: true,
      isDraft: isDraft,
      offerId: offer.nonHumanizedId,
    })
  }

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
    offer.stocks.filter(stock => stock.remainingQuantity === 0).length

  const shouldShowIndividualWarning =
    audience === Audience.INDIVIDUAL &&
    computeNumberOfSoldOutStocks() > 0 &&
    offer.status !== OFFER_STATUS_SOLD_OUT

  const shouldShowCollectiveWarning =
    audience === Audience.COLLECTIVE &&
    offer.educationalBooking?.booking_status === OFFER_STATUS_PENDING &&
    shouldDisplayWarning(offer.stocks)

  return (
    <td className={styles['title-column']}>
      {offer.isShowcase && (
        <Tag label="Offre vitrine" className={styles['offer-template-tag']} />
      )}
      <Link
        className={styles['name']}
        title={`${offer.name} - éditer l’offre`}
        onClick={onOfferNameClick}
        to={editionOfferLink}
      >
        {offer.name}
      </Link>
      {offer.isEvent && (
        <span className={styles['stocks']}>
          {getDateInformations()}
          {shouldShowIndividualWarning && (
            <div>
              <Icon
                className={styles['sold-out-icon']}
                svg="ico-warning"
                alt="Attention"
              />

              <span className={styles['sold-out-dates']}>
                <Icon
                  className={styles['sold-out-icon']}
                  svg="ico-warning"
                  alt="Attention"
                />
                {pluralize(computeNumberOfSoldOutStocks(), 'date épuisée')}
              </span>
            </div>
          )}
          {shouldShowCollectiveWarning && (
            <div className={styles['sold-out']}>
              <AlertFilledIcon
                className={styles['sold-out-icon']}
                title="Attention"
              />

              <span className={styles['sold-out-dates']}>
                La date limite de réservation par le chef d'établissement est
                dans{' '}
                {`${
                  getRemainingTime(offer.stocks) >= 1
                    ? pluralize(getRemainingTime(offer.stocks), 'jour')
                    : "moins d'un jour"
                } (${getDate(offer.stocks)})`}
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
