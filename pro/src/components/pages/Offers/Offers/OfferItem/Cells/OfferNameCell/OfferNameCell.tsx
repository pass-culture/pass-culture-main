import React from 'react'
import { Link } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_SOLD_OUT } from 'core/Offers'
import { Offer } from 'core/Offers/types'
import { ReactComponent as WarningStocksIcon } from 'icons/ico-warning-stocks.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { Tag } from 'ui-kit'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'
import { pluralize } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

import styles from '../../OfferItem.module.scss'

interface OfferNameCellProps {
  offer: Offer
  editionOfferLink: string
}

const OfferNameCell = ({ offer, editionOfferLink }: OfferNameCellProps) => {
  const { logEvent } = useAnalytics()

  const onOfferNameClick = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_FORM_NAVIGATION_IN.OFFERS,
      to: OfferBreadcrumbStep.SUMMARY,
      used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_TITLE,
      isEdition: true,
    })
  }

  const getDateInformations = () => {
    const {
      stocks,
      venue: { departementCode },
    } = offer
    const { beginningDatetime } = stocks[0] || {}
    if (offer.isShowcase) {
      return 'Date et prix à définir'
    }
    if (!beginningDatetime || !departementCode) {
      return null
    }

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

  const shouldShowSoldOutWarning =
    computeNumberOfSoldOutStocks() > 0 && offer.status !== OFFER_STATUS_SOLD_OUT

  return (
    <td className={styles['title-column']}>
      {offer.isShowcase && (
        <Tag label="Offre vitrine" className={styles['offer-template-tag']} />
      )}
      <Link
        className={styles['name']}
        title={`${offer.name} - éditer l'offre`}
        onClick={onOfferNameClick}
        to={editionOfferLink}
      >
        {offer.name}
      </Link>
      {offer.isEvent && (
        <span className={styles['stocks']}>
          {getDateInformations()}
          {shouldShowSoldOutWarning && (
            <div>
              <WarningStocksIcon
                title=""
                className={styles['sold-out-icon']}
                tabIndex={0}
              />

              <span className={styles['sold-out-dates']}>
                <WarningStocksIcon title="" />
                {pluralize(computeNumberOfSoldOutStocks(), 'date épuisée')}
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
