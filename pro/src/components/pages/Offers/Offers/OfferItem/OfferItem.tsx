import React from 'react'
import { Link } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'components/hooks/useOfferEditionURL'
import Icon from 'components/layout/Icon'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import StatusLabel from 'components/pages/Offers/Offer/OfferStatus/StatusLabel'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { computeVenueDisplayName } from 'repository/venuesService'

import OfferNameCell from './Cells/OfferNameCell'
import ThumbCell from './Cells/ThumbCell'

export type OfferItemProps = {
  disabled?: boolean
  isSelected?: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  audience: Audience
}

const OfferItem = ({
  disabled = false,
  offer,
  isSelected = false,
  selectOffer,
  audience,
}: OfferItemProps) => {
  const { venue, stocks, id, isEducational, isShowcase } = offer
  const { logEvent } = useAnalytics()
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const editionOfferLink = useOfferEditionURL(
    isEducational,
    id,
    isOfferFormV3,
    !!isShowcase
  )
  const editionStockLink = useOfferStockEditionURL(
    isEducational,
    id,
    !!isShowcase
  )

  function handleOnChangeSelected() {
    selectOffer(offer.id, !isSelected, !!isShowcase)
  }

  const computeRemainingStockOrEducationalInstitutionValue = (
    stocks: Offer['stocks']
  ) => {
    if (audience === Audience.COLLECTIVE) {
      return offer.educationalInstitution?.name ?? 'Tous les établissements'
    }

    let totalRemainingStock = 0
    for (const stock of stocks) {
      if (stock.remainingQuantity === 'unlimited') {
        return 'Illimité'
      }
      totalRemainingStock += Number(stock.remainingQuantity)
    }

    return totalRemainingStock
  }

  const isOfferEditable = offer ? offer.isEditable : null
  const isOfferInactiveOrExpiredOrDisabled =
    !offer.isActive ||
    offer.hasBookingLimitDatetimesPassed ||
    isOfferDisabled(offer.status)

  return (
    <tr
      className={`offer-item ${
        isOfferInactiveOrExpiredOrDisabled ? 'inactive' : ''
      } offer-row`}
    >
      <td className="select-column">
        <input
          checked={isSelected}
          className="select-offer-checkbox"
          data-testid={`select-offer-${offer.id}`}
          disabled={disabled || isOfferDisabled(offer.status)}
          id={`select-offer-${offer.id}`}
          onChange={handleOnChangeSelected}
          type="checkbox"
        />
      </td>
      {audience === Audience.INDIVIDUAL && (
        <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />
      )}
      <OfferNameCell offer={offer} editionOfferLink={editionOfferLink} />
      <td className="venue-column">
        {venue && computeVenueDisplayName(venue)}
      </td>
      <td className="stock-column">
        {computeRemainingStockOrEducationalInstitutionValue(stocks)}
      </td>
      <td className="status-column">
        <StatusLabel status={offer.status} />
      </td>
      <td className="switch-column">
        <Link
          className="secondary-link with-icon"
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_FORM_NAVIGATION_IN.OFFERS,
              to: OfferBreadcrumbStep.STOCKS,
              used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_STOCKS,
              isEdition: true,
            })
          }
          to={editionStockLink}
        >
          <Icon svg="ico-guichet-full" />
          Stocks
        </Link>
      </td>
      <td className="edit-column">
        {isOfferEditable && (
          <Link
            className="secondary-link"
            onClick={() =>
              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OFFER_FORM_NAVIGATION_IN.OFFERS,
                to: OfferBreadcrumbStep.SUMMARY,
                used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_PEN,
                isEdition: true,
              })
            }
            to={editionOfferLink}
          >
            <Icon alt={`${offer.name} - éditer l'offre`} svg="ico-pen" />
          </Link>
        )}
      </td>
    </tr>
  )
}

export default OfferItem
