import { format } from 'date-fns-tz'
import React from 'react'
import { Link } from 'react-router-dom'

import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
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
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as WarningIcon } from 'icons/ico-warning.svg'
import { Tag } from 'ui-kit'
import {
  FORMAT_DD_MM_YYYY_HH_mm,
  FORMAT_DD_MM_YYYY,
  toDateStrippedOfTimezone,
} from 'utils/date'
import { pluralize } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

import styles from '../../OfferItem.module.scss'

interface OfferNameCellProps {
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
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')

  const onOfferNameClick = () => {
    const isDraft = offer.status === OFFER_STATUS_DRAFT
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_FORM_NAVIGATION_IN.OFFERS,
      to: !isDraft
        ? OfferBreadcrumbStep.SUMMARY
        : isOfferFormV3
        ? OFFER_WIZARD_STEP_IDS.INFORMATIONS
        : OfferBreadcrumbStep.DETAILS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_TITLE,
      isEdition: true,
      isDraft: isDraft,
      offerId: offer.id,
    })
  }

  const getDateInformations = () => {
    const {
      stocks,
      venue: { departementCode },
    } = offer
    const { beginningDatetime } = stocks[0] || {}
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

  const isImproveCollectiveStatusActive = useActiveFeature(
    'WIP_IMPROVE_COLLECTIVE_STATUS'
  )

  const shouldShowIndividualWarning =
    audience === Audience.INDIVIDUAL &&
    computeNumberOfSoldOutStocks() > 0 &&
    offer.status !== OFFER_STATUS_SOLD_OUT

  const getRemainingTime = () => {
    const { stocks } = offer
    const { bookingLimitDatetime } = stocks[0] || {}

    if (!bookingLimitDatetime) {
      return -1
    }

    const date = new Date()

    const time_diff = bookingLimitDatetime.getTime() - date.getTime()
    const days_Diff = time_diff / (1000 * 3600 * 24)

    if (days_Diff >= 7) {
      return -1
    }
    return Math.floor(days_Diff)
  }

  const getDate = () => {
    const { stocks } = offer
    const { bookingLimitDatetime } = stocks[0] || {}

    if (!bookingLimitDatetime) {
      return false
    }

    return format(
      toDateStrippedOfTimezone(bookingLimitDatetime.toString()),
      FORMAT_DD_MM_YYYY
    )
  }

  const shouldShowCollectiveWarning =
    isImproveCollectiveStatusActive &&
    audience === Audience.COLLECTIVE &&
    offer.educationalBooking?.booking_status === OFFER_STATUS_PENDING &&
    getRemainingTime() > 0

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
              <WarningIcon
                title=""
                className={styles['sold-out-icon']}
                tabIndex={0}
              />

              <span className={styles['sold-out-dates']}>
                <WarningIcon title="" />
                {pluralize(computeNumberOfSoldOutStocks(), 'date épuisée')}
              </span>
            </div>
          )}
          {shouldShowCollectiveWarning && (
            <div>
              <WarningIcon
                title=""
                className={styles['sold-out-icon']}
                tabIndex={0}
              />

              <span className={styles['sold-out-dates']}>
                La date limite de réservation par le chef d'établissement est
                dans {`${pluralize(getRemainingTime(), 'jour')} (${getDate()})`}
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
