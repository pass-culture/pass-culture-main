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
import { FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'
import { pluralize } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

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
    if (offer.isShowcase) {
      return 'Date et prix à définir'
    }
    const stockSize = offer.stocks ? offer.stocks.length : 0
    return stockSize === 1
      ? formatLocalTimeDateString(
          offer.stocks[0].beginningDatetime,
          offer.venue.departementCode,
          FORMAT_DD_MM_YYYY_HH_mm
        )
      : pluralize(stockSize, 'date')
  }

  const computeNumberOfSoldOutStocks = () =>
    offer.stocks.filter(stock => stock.remainingQuantity === 0).length

  const shouldShowSoldOutWarning =
    computeNumberOfSoldOutStocks() > 0 && offer.status !== OFFER_STATUS_SOLD_OUT

  return (
    <td className="title-column">
      <Link
        className="name"
        title={`${name} - éditer l'offre`}
        onClick={onOfferNameClick}
        to={editionOfferLink}
      >
        {offer.name}
      </Link>
      {offer.isEvent && (
        <span className="stocks">
          {getDateInformations()}
          {shouldShowSoldOutWarning && (
            <div>
              <WarningStocksIcon
                title=""
                className="sold-out-icon"
                tabIndex={0}
              />

              <span className="sold-out-dates">
                <WarningStocksIcon title="" className="ico-warning-stocks" />
                {pluralize(computeNumberOfSoldOutStocks(), 'date épuisée')}
              </span>
            </div>
          )}
        </span>
      )}
      {offer.productIsbn && <div className="isbn">{offer.productIsbn}</div>}
    </td>
  )
}

export default OfferNameCell
