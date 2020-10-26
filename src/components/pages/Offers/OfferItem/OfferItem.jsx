import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import Thumb from 'components/layout/Thumb'
import { isOfferFullyBooked } from 'components/pages/Offers/domain/isOfferFullyBooked'
import { computeVenueDisplayName } from 'repository/venuesService'
import { fetchFromApiWithCredentials } from 'utils/fetch'
import { pluralize } from 'utils/pluralize'

import { computeOfferStatus } from '../domain/computeOfferStatus'
import { OFFER_STATUS } from '../domain/offerStatus'

const OFFER_STATUS_PROPERTIES = {
  [OFFER_STATUS.INACTIVE]: {
    className: 'status-inactive',
    icon: 'ico-status-inactive',
  },
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
}

const OfferItem = ({
  areAllOffersSelected,
  offer,
  refreshOffers,
  stocks,
  trackActivateOffer,
  trackDeactivateOffer,
  venue,
  isSelected,
  selectOffer,
}) => {
  function handleOnDeactivateClick() {
    const { id, isActive } = offer || {}
    const body = {
      ids: [id],
      isActive: !isActive,
    }

    fetchFromApiWithCredentials('/offers/active-status', 'PATCH', body).then(() => {
      refreshOffers({ shouldTriggerSpinner: false })
    })

    isActive ? trackDeactivateOffer(id) : trackActivateOffer(id)
  }

  function handleOnChangeSelected() {
    selectOffer(offer.id, !isSelected)
  }

  const buildStocksDetail = (offer, stockSize) => {
    if (offer.isThing) {
      return `${stockSize} prix`
    }

    if (offer.isEvent) {
      return pluralize(stockSize, 'date')
    }
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
          checked={isSelected || areAllOffersSelected}
          className="select-offer-checkbox"
          data-testid={`select-offer-${offer.id}`}
          disabled={areAllOffersSelected}
          id={`select-offer-${offer.id}`}
          onChange={handleOnChangeSelected}
          type="checkbox"
        />
      </td>
      <td className="thumb-column">
        <Thumb url={offer.thumbUrl} />
      </td>
      <td className="title-column">
        <Link
          className="name"
          title="Afficher le détail de l'offre"
          to={`/offres/${offer.id}`}
        >
          {offer.name}
        </Link>
        <span className="stocks">
          <Link
            className="quaternary-link"
            title="Afficher le détail des stocks"
            to={`/offres/${offer.id}?gestion`}
          >
            {buildStocksDetail(offer, stockSize)}
          </Link>
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
        <button
          className="secondary-button"
          onClick={handleOnDeactivateClick}
          type="button"
        >
          {offer.isActive ? 'Désactiver' : 'Activer'}
        </button>
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
  isSelected: false,
}

OfferItem.propTypes = {
  isSelected: PropTypes.bool,
  offer: PropTypes.shape().isRequired,
  refreshOffers: PropTypes.func.isRequired,
  selectOffer: PropTypes.func.isRequired,
  stocks: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  trackActivateOffer: PropTypes.func.isRequired,
  trackDeactivateOffer: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    isVirtual: PropTypes.bool.isRequired,
    name: PropTypes.string,
    offererName: PropTypes.string,
    publicName: PropTypes.string,
  }).isRequired,
}

export default OfferItem
