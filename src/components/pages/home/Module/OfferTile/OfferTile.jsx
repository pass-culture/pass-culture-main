import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { formatSearchResultDate } from '../../../../../utils/date/date'
import { formatResultPrice } from '../../../../../utils/price'
import { DEFAULT_THUMB_URL } from '../../../../../utils/thumb'

export const noOp = () => false

const OfferTile = ({ historyPush, hit, isSwitching }) => {
  const { offer, venue } = hit
  const offerDates = offer.isEvent
    ? `${formatSearchResultDate(venue.departementCode, offer.dates)} - `
    : ''
  const formattedPrice = formatResultPrice(offer.priceMin, offer.priceMax, offer.isDuo)
  function goToOffer() {
    if (!isSwitching) {
      historyPush(`/offre/details/${offer.id}`)
    }
  }
  function preventDefault(event) {
    event.preventDefault()
  }

  return (
    <li
      className="offer-tile-wrapper"
      key={offer.id}
    >
      <Link
        onClick={goToOffer}
        onMouseDown={preventDefault}
        to={noOp}
      >
        <div className="otw-image-wrapper">
          <img
            alt=""
            src={offer.thumbUrl ? offer.thumbUrl : DEFAULT_THUMB_URL}
          />
          <div className="otw-offer-linear-background">
            <div className="otw-offer-name">
              {offer.name}
            </div>
          </div>
        </div>
        <p className="otw-venue">
          {venue.name}
        </p>
        <p className="otw-offer-info">
          <span>
            {offerDates}
          </span>
          <span>
            {formattedPrice}
          </span>
        </p>
      </Link>
    </li>
  )
}

OfferTile.propTypes = {
  historyPush: PropTypes.func.isRequired,
  hit: PropTypes.shape().isRequired,
  isSwitching: PropTypes.bool.isRequired,
}

export default OfferTile
