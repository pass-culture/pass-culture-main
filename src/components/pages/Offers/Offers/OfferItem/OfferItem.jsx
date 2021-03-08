import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import Thumb from 'components/layout/Thumb'
import { isOfferFullyBooked } from 'components/pages/Offers/Offers/domain/isOfferFullyBooked'
import { computeVenueDisplayName } from 'repository/venuesService'
import { pluralize } from 'utils/pluralize'

import { computeOfferStatus } from '../domain/computeOfferStatus'
import { OFFER_STATUS } from '../domain/offerStatus'

const OFFER_STATUS_PROPERTIES = {
  [OFFER_STATUS.EXPIRED]: {
    className: 'status-expired',
    icon: 'ico-status-expired',
  },
  [OFFER_STATUS.SOLD_OUT]: {
    className: 'status-sold-out',
    icon: 'ico-status-sold-out',
  },
  [OFFER_STATUS.ACTIVE]: {
    className: 'status-active',
    icon: 'ico-status-validated',
  },
  [OFFER_STATUS.REJECTED]: {
    className: 'status-rejected',
    icon: 'ico-status-rejected',
  },
  [OFFER_STATUS.AWAITING]: {
    className: 'status-awaiting',
    icon: 'ico-status-awaiting',
  },
  [OFFER_STATUS.VALIDATED]: {
    className: 'status-validated',
    icon: 'ico-status-validated',
  },
}

const OfferItem = ({ disabled, offer, stocks, venue, isSelected, selectOffer }) => {
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
  const isOfferInactiveOrExpired = !offer.isActive || offer.hasBookingLimitDatetimesPassed
  const shouldShowSoldOutWarning =
    computeNumberOfSoldOutStocks(stocks) > 0 && !isOfferFullyBooked(stocks)
  const offerStatus = computeOfferStatus(offer, stocks)

  return (
    <tr className={`offer-item ${isOfferInactiveOrExpired ? 'inactive' : ''} offer-row`}>
      <td className="select-column">
        <input
          checked={isSelected}
          className="select-offer-checkbox"
          data-testid={`select-offer-${offer.id}`}
          disabled={disabled}
          id={`select-offer-${offer.id}`}
          onChange={handleOnChangeSelected}
          type="checkbox"
        />
      </td>
      <td className="thumb-column">
        <Link
          className="name"
          title="Afficher le détail de l'offre"
          to={`/offres/${offer.id}/edition`}
        >
          <Thumb
            alt="Miniature d'offre"
            url={offer.thumbUrl}
          />
        </Link>
      </td>
      <td className="title-column">
        <Link
          className="name"
          title="Afficher le détail de l'offre"
          to={`/offres/${offer.id}/edition`}
        >
          {offer.name}
        </Link>
        {offer.isEvent && (
          <span className="stocks">
            {pluralize(stockSize, 'date')}
            {shouldShowSoldOutWarning && (
              <div>
                <Icon
                  className="sold-out-icon"
                  svg="ico-warning-stocks"
                  tabIndex={0}
                />
                <span className="sold-out-dates">
                  <Icon svg="ico-warning-stocks" />
                  {pluralize(computeNumberOfSoldOutStocks(stocks), 'date épuisée')}
                </span>
              </div>
            )}
          </span>
        )}
      </td>
      <td className="venue-column">
        {venue && computeVenueDisplayName(venue)}
      </td>
      <td className="stock-column">
        {computeRemainingStockValue(stocks)}
      </td>
      <td className="status-column">
        <span className={OFFER_STATUS_PROPERTIES[offerStatus].className}>
          <Icon svg={OFFER_STATUS_PROPERTIES[offerStatus].icon} />
          {offerStatus}
        </span>
      </td>
      <td className="switch-column">
        <Link
          className="secondary-link with-icon"
          to={`/offres/${offer.id}/stocks`}
        >
          <Icon svg="ico-guichet-full" />
          {'Stocks'}
        </Link>
      </td>
      <td className="edit-column">
        {isOfferEditable && (
          <Link
            className="secondary-link"
            to={`/offres/${offer.id}/edition`}
          >
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
  offer: PropTypes.shape().isRequired,
  selectOffer: PropTypes.func.isRequired,
  stocks: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  venue: PropTypes.shape({
    isVirtual: PropTypes.bool.isRequired,
    name: PropTypes.string,
    offererName: PropTypes.string,
    publicName: PropTypes.string,
  }).isRequired,
}

export default OfferItem
