import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import useOfferEditionURL from 'components/hooks/useOfferEditionURL'
import Icon from 'components/layout/Icon'
import Thumb from 'components/layout/Thumb'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import StatusLabel from 'components/pages/Offers/Offer/OfferStatus/StatusLabel'
import { OFFER_STATUS_SOLD_OUT } from 'components/pages/Offers/Offers/_constants'
import { computeVenueDisplayName } from 'repository/venuesService'
import { Tag } from 'ui-kit'
import { pluralize } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

import useOfferStockEditionURL from '../../../../hooks/useOfferStockEditionURL'

const OfferItem = ({ disabled, offer, isSelected, selectOffer }) => {
  const { venue, stocks, id, isEducational, isShowcase } = offer

  const editionOfferLink = useOfferEditionURL(isEducational, id)
  const editionStockLink = useOfferStockEditionURL(isEducational, id)

  function handleOnChangeSelected() {
    selectOffer(offer.id, !isSelected)
  }

  const computeNumberOfSoldOutStocks = () =>
    stocks.filter(stock => stock.remainingQuantity === 0).length

  const computeRemainingStockValue = stocks => {
    let totalRemainingStock = 0
    for (const stock of stocks) {
      if (stock.remainingQuantity === 'unlimited') {
        return 'Illimité'
      }
      totalRemainingStock += stock.remainingQuantity
    }

    return totalRemainingStock
  }

  const stockSize = stocks ? stocks.length : null
  const isOfferEditable = offer ? offer.isEditable : null
  const isOfferInactiveOrExpiredOrDisabled =
    !offer.isActive ||
    offer.hasBookingLimitDatetimesPassed ||
    isOfferDisabled(offer.status)
  const shouldShowSoldOutWarning =
    computeNumberOfSoldOutStocks(stocks) > 0 &&
    offer.status !== OFFER_STATUS_SOLD_OUT

  const getDateInformations = () => {
    if (isShowcase) {
      return 'Date et prix à définir'
    }
    return stockSize === 1
      ? formatLocalTimeDateString(
          stocks[0].beginningDatetime,
          venue.departementCode,
          'dd/MM/yyyy HH:mm'
        )
      : pluralize(stockSize, 'date')
  }

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
      <td className="thumb-column">
        <Link
          className="name"
          title="Afficher les détails de l'offre"
          to={editionOfferLink}
        >
          <Thumb alt="Miniature d'offre" url={offer.thumbUrl} />
        </Link>
      </td>
      <td className="title-column">
        {offer.isEducational && (
          <Tag className="educational-tag">Offre collective</Tag>
        )}
        <Link
          className="name"
          title="Afficher les détails de l'offre"
          to={editionOfferLink}
        >
          {offer.name}
        </Link>
        {offer.isEvent && (
          <span className="stocks">
            {getDateInformations()}
            {shouldShowSoldOutWarning && (
              <div>
                <Icon
                  className="sold-out-icon"
                  svg="ico-warning-stocks"
                  tabIndex={0}
                />
                <span className="sold-out-dates">
                  <Icon svg="ico-warning-stocks" />
                  {pluralize(
                    computeNumberOfSoldOutStocks(stocks),
                    'date épuisée'
                  )}
                </span>
              </div>
            )}
          </span>
        )}
        {offer.productIsbn && <div className="isbn">{offer.productIsbn}</div>}
      </td>
      <td className="venue-column">
        {venue && computeVenueDisplayName(venue)}
      </td>
      <td className="stock-column">{computeRemainingStockValue(stocks)}</td>
      <td className="status-column">
        <StatusLabel status={offer.status} />
      </td>
      <td className="switch-column">
        <Link className="secondary-link with-icon" to={editionStockLink}>
          <Icon svg="ico-guichet-full" />
          Stocks
        </Link>
      </td>
      <td className="edit-column">
        {isOfferEditable && (
          <Link className="secondary-link" to={editionOfferLink}>
            <Icon svg="ico-pen" />
          </Link>
        )}
      </td>
    </tr>
  )
}

OfferItem.defaultProps = {
  disabled: false,
  isSelected: false,
}

OfferItem.propTypes = {
  disabled: PropTypes.bool,
  isSelected: PropTypes.bool,
  offer: PropTypes.shape({
    venue: PropTypes.shape({
      name: PropTypes.string,
      publicName: PropTypes.string,
      offererName: PropTypes.string,
      isVirtual: PropTypes.bool,
      departementCode: PropTypes.string,
    }),
    stocks: PropTypes.arrayOf(
      PropTypes.shape({
        beginningDatetime: PropTypes.string,
        remainingQuantity: PropTypes.number,
      })
    ),
    id: PropTypes.string,
    isEditable: PropTypes.bool,
    isActive: PropTypes.bool,
    hasBookingLimitDatetimesPassed: PropTypes.bool,
    status: PropTypes.string,
    thumbUrl: PropTypes.string,
    name: PropTypes.string,
    isEvent: PropTypes.bool,
    productIsbn: PropTypes.string,
    isEducational: PropTypes.bool,
    isShowcase: PropTypes.bool,
  }).isRequired,
  selectOffer: PropTypes.func.isRequired,
}

export default OfferItem
